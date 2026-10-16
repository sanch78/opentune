from dataclasses import replace
from threading import Event

import numpy as np
import pytest

from opentune.audio import AudioError, PortAudio


class FakeAPI:
    class CallbackStop(Exception):
        pass

    class CallbackAbort(Exception):
        pass

    def __init__(self):
        self.devices = [
            {"name": "HDMI monitor", "hostapi": 0, "max_input_channels": 0,
             "max_output_channels": 2, "default_samplerate": 48000},
            {"name": "Microphone", "hostapi": 0, "max_input_channels": 1,
             "max_output_channels": 0, "default_samplerate": 48000},
        ]
        self.streams = []
        self.output_checks = []
        self.input_checks = []
        self.fail_output = False
        self.fail_input = False
        self.start_error = False
        self.open_error = False
        self.callback_status = False
        self.latency = 0.05
        self.actual_rate = 48000
        self.on_start = None
        self.silent_stall = False

    def query_devices(self):
        return self.devices

    def query_hostapis(self):
        return [{"name": "Windows WASAPI"}, {"name": "MME"}]

    def WasapiSettings(self, **kwargs):
        return kwargs

    def check_output_settings(self, **kwargs):
        self.output_checks.append(kwargs)
        if self.fail_output:
            raise RuntimeError("unsupported format")

    def check_input_settings(self, **kwargs):
        self.input_checks.append(kwargs)
        if self.fail_input:
            raise RuntimeError("input unavailable")

    def OutputStream(self, **kwargs):
        if self.open_error:
            raise RuntimeError("device disconnected")
        api = self

        class Stream:
            samplerate = api.actual_rate
            latency = api.latency

            def __init__(self):
                self.closed = False
                self.aborted = False
                self.started = False
                self.buffers = []

            def start(self):
                self.started = True
                if api.start_error:
                    raise RuntimeError("start failed")
                if api.on_start:
                    api.on_start()
                if api.silent_stall:
                    return
                try:
                    for _ in range(100):
                        data = np.full((1024, 2), np.nan, dtype=np.float32)
                        try:
                            kwargs["callback"](data, len(data), None, api.callback_status)
                        finally:
                            self.buffers.append(data.copy())
                except (api.CallbackStop, api.CallbackAbort):
                    kwargs["finished_callback"]()

            def abort(self):
                self.aborted = True

            def close(self):
                self.closed = True

        stream = Stream()
        self.streams.append((stream, kwargs))
        return stream


@pytest.fixture
def setup():
    api = FakeAPI()
    audio = PortAudio(api, platform="win32")
    output, mic = audio.discover()
    return api, audio, output, mic


def test_discovery_is_read_only_and_preserves_host_information(setup):
    api, audio, output, mic = setup
    assert output.host_name == "Windows WASAPI" and mic.inputs == 1
    assert not api.streams and not api.output_checks and not api.input_checks


def test_silent_probe_uses_explicit_shared_stereo_and_warns_about_duplex(setup):
    api, audio, output, mic = setup
    probe = audio.probe(output, mic, 48000)
    assert "NOT verified" in probe.input_status
    assert api.output_checks[0] == dict(device=0, channels=2, dtype="float32", samplerate=48000,
                                      extra_settings={"exclusive": False, "auto_convert": False})
    assert not api.streams


def test_mismatched_hosts_not_reported_as_measurement_pair(setup):
    api, audio, output, mic = setup
    api.devices[1]["hostapi"] = 1
    mic = audio.discover()[1]
    assert "host APIs differ" in audio.probe(output, mic, 48000).input_status
    assert not api.input_checks


@pytest.mark.parametrize("mutation", ["removed", "renamed", "negative", "non-wasapi", "mono"])
def test_invalid_or_changed_output_never_opens_stream(setup, mutation):
    api, audio, output, mic = setup
    if mutation == "removed":
        api.devices.clear()
    elif mutation == "renamed":
        api.devices[0]["name"] = "Another output"
    elif mutation == "negative":
        output = replace(output, index=-1)
    elif mutation == "non-wasapi":
        output = replace(output, host_name="MME")
    else:
        output = replace(output, outputs=1)
    with pytest.raises(AudioError):
        audio.play_channel(output, 48000, "left", -48, Event())
    assert not api.streams


def test_unsupported_output_does_not_fall_back(setup):
    api, audio, output, mic = setup
    api.fail_output = True
    with pytest.raises(AudioError, match="Stereo output"):
        audio.play_channel(output, 48000, "left", -48, Event())
    assert not api.streams and len(api.output_checks) == 1


def test_input_failure_is_separate_from_playback_support(setup):
    api, audio, output, mic = setup
    api.fail_input = True
    assert "unavailable" in audio.probe(output, mic, 48000).input_status
    assert not api.streams


def test_playback_is_finite_stereo_and_cleanup_is_unconditional(setup):
    api, audio, output, mic = setup
    result = audio.play_channel(output, 48000, "right", -48, Event())
    stream, settings = api.streams[0]
    assert not result.cancelled and result.rate == 48000
    assert stream.closed and stream.aborted
    assert settings["device"] == output.index and settings["channels"] == 2
    data = np.concatenate(stream.buffers)
    assert np.isfinite(data).all() and np.count_nonzero(data[:, 0]) == 0
    assert np.count_nonzero(data[:, 1]) > 0
    assert np.all(data[-1] == 0)  # last partial callback is padded with silence


def test_cancel_before_playback_opens_nothing(setup):
    api, audio, output, mic = setup
    cancel = Event()
    cancel.set()
    assert audio.play_channel(output, 48000, "left", -48, cancel).cancelled
    assert not api.streams


def test_cancel_during_playback_aborts_and_silences_buffer(setup):
    api, audio, output, mic = setup
    cancel = Event()
    api.on_start = cancel.set
    assert audio.play_channel(output, 48000, "left", -48, cancel).cancelled
    stream, _ = api.streams[0]
    assert stream.closed and stream.aborted
    assert all(np.count_nonzero(buffer) == 0 for buffer in stream.buffers)


@pytest.mark.parametrize("failure", ["open_error", "start_error", "callback_status"])
def test_stream_failure_surfaces_and_releases_resources(setup, failure):
    api, audio, output, mic = setup
    setattr(api, failure, True)
    with pytest.raises(AudioError):
        audio.play_channel(output, 48000, "left", -48, Event())
    assert len(api.streams) <= 1
    for stream, _ in api.streams:
        assert stream.closed and stream.aborted


@pytest.mark.parametrize("latency,rate", [(1.0, 48000), (float("nan"), 48000), (0.05, 44100)])
def test_stream_with_unexpected_rate_or_long_latency_never_starts(setup, latency, rate):
    api, audio, output, mic = setup
    api.latency, api.actual_rate = latency, rate
    with pytest.raises(AudioError):
        audio.play_channel(output, 48000, "left", -48, Event())
    stream, _ = api.streams[0]
    assert not stream.started and stream.closed


def test_disconnected_or_stalled_stream_times_out_and_closes(setup, monkeypatch):
    api, audio, output, mic = setup
    api.silent_stall = True
    clock = iter((0.0, 10.0))
    monkeypatch.setattr("opentune.audio.time.monotonic", lambda: next(clock))
    with pytest.raises(AudioError, match="did not finish"):
        audio.play_channel(output, 48000, "left", -48, Event())
    stream, _ = api.streams[0]
    assert stream.aborted and stream.closed
