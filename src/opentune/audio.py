"""PortAudio adapter. Importing this module does not initialize audio hardware."""

from dataclasses import dataclass
import math
import sys
from threading import Event
import time

from opentune.signals import CHECK_RATES, channel_tone


class AudioError(RuntimeError):
    """A route cannot be used safely; do not substitute the default device."""


@dataclass(frozen=True)
class Device:
    """Process-local PortAudio identity. Never persist its index as an endpoint ID."""

    index: int
    name: str
    host_index: int
    host_name: str
    inputs: int
    outputs: int
    default_rate: float

    @property
    def label(self) -> str:
        return f"{self.name} [{self.host_name}; ID {self.index}]"


@dataclass(frozen=True)
class RouteProbe:
    rate: int
    input_status: str


@dataclass(frozen=True)
class PlaybackResult:
    cancelled: bool
    rate: float | None = None
    latency: float | None = None


class PortAudio:
    def __init__(self, api=None, platform: str | None = None):
        self._api = api
        self.platform = sys.platform if platform is None else platform

    @property
    def api(self):
        if self._api is None:
            try:
                import sounddevice
            except (ImportError, OSError) as exc:
                raise AudioError(f"PortAudio is unavailable: {exc}") from exc
            self._api = sounddevice
        return self._api

    def discover(self) -> tuple[Device, ...]:
        """Enumerate only. No stream, recording, playback, or default-route change."""
        try:
            hosts = self.api.query_hostapis()
            return tuple(
                Device(index, str(item["name"]), int(item["hostapi"]),
                       str(hosts[item["hostapi"]]["name"]),
                       int(item["max_input_channels"]), int(item["max_output_channels"]),
                       float(item["default_samplerate"]))
                for index, item in enumerate(self.api.query_devices())
            )
        except AudioError:
            raise
        except Exception as exc:
            raise AudioError(f"Device discovery failed: {exc}") from exc

    def check_output_device(self, device: Device) -> None:
        if device.outputs < 2:
            raise AudioError("Select an output with at least two channels.")
        if self.platform == "win32" and device.host_name != "Windows WASAPI":
            raise AudioError("This Windows prototype requires a Windows WASAPI output.")
        current = self.discover()
        if not 0 <= device.index < len(current) or current[device.index] != device:
            raise AudioError("The selected output changed. Refresh and select it again.")

    def _settings(self, device: Device):
        if device.host_name == "Windows WASAPI":
            # No exclusive path or automatic sample-rate/channel conversion.
            return self.api.WasapiSettings(exclusive=False, auto_convert=False)
        return None

    def probe(self, output: Device, microphone: Device | None, rate: int) -> RouteProbe:
        """Probe formats without opening streams. Input support is not duplex proof."""
        if rate not in CHECK_RATES:
            raise AudioError("Select 48,000 or 44,100 Hz for this prototype.")
        self.check_output_device(output)
        try:
            self.api.check_output_settings(device=output.index, channels=2,
                                           dtype="float32", samplerate=rate,
                                           extra_settings=self._settings(output))
        except Exception as exc:
            raise AudioError(f"Stereo output at {rate} Hz is unavailable: {exc}") from exc
        status = "No microphone selected; playback does not require one."
        if microphone is not None:
            current = self.discover()
            if not 0 <= microphone.index < len(current) or current[microphone.index] != microphone:
                status = "Input changed; refresh and select it again."
            elif microphone.inputs < 1:
                status = "Selected device has no input channel."
            elif microphone.host_index != output.host_index:
                status = "Input/output host APIs differ; no single-stream measurement pairing."
            else:
                try:
                    self.api.check_input_settings(device=microphone.index, channels=1,
                                                  dtype="float32", samplerate=rate,
                                                  extra_settings=self._settings(microphone))
                    status = "Mono input format supported; duplex capture and clocks NOT verified."
                except Exception as exc:
                    status = f"Mono input format unavailable: {exc}"
        return RouteProbe(rate, status)

    def play_channel(self, output: Device, rate: int, channel: str, level: int,
                     cancel: Event) -> PlaybackResult:
        """Play one finite signal. Cancellation/failure aborts, never reroutes.

        Only bounded buffer copies and status flags run in the PortAudio callback.
        A worker owns stream lifecycle and monitors cancellation and completion.
        """
        data = channel_tone(channel, rate, level)
        if cancel.is_set():
            return PlaybackResult(True)
        self.probe(output, None, rate)
        position = 0
        callback_problem = False
        done = Event()
        stream = None
        callback_abort, callback_stop = self.api.CallbackAbort, self.api.CallbackStop

        def callback(outdata, frames, timing, status):
            nonlocal position, callback_problem
            outdata.fill(0)
            if cancel.is_set():
                raise callback_abort
            if status:
                callback_problem = True
                raise callback_abort
            count = min(frames, len(data) - position)
            outdata[:count] = data[position:position + count]
            position += count
            if position == len(data):
                raise callback_stop

        try:
            if cancel.is_set():
                return PlaybackResult(True)
            stream = self.api.OutputStream(
                device=output.index, samplerate=rate, channels=2, dtype="float32",
                latency=0.05, blocksize=0, extra_settings=self._settings(output),
                callback=callback, finished_callback=done.set,
            )
            if cancel.is_set():
                return PlaybackResult(True)
            actual_rate, latency = float(stream.samplerate), float(stream.latency)
            if not math.isfinite(actual_rate) or abs(actual_rate - rate) > 1:
                raise AudioError("The stream rate differs from the requested rate.")
            if not math.isfinite(latency) or not 0 <= latency <= 0.5:
                raise AudioError("Output latency exceeds this prototype's 0.5 second limit.")
            stream.start()
            deadline = time.monotonic() + len(data) / rate + latency + 2
            while not done.wait(0.01):
                if cancel.is_set():
                    return PlaybackResult(True, actual_rate, latency)
                if time.monotonic() > deadline:
                    raise AudioError("Output did not finish in time; route needs rechecking.")
            if cancel.is_set():
                return PlaybackResult(True, actual_rate, latency)
            if callback_problem or position != len(data):
                raise AudioError("Playback dropped out or ended early. Refresh and recheck the route.")
            return PlaybackResult(False, actual_rate, latency)
        except AudioError:
            raise
        except Exception as exc:
            raise AudioError(f"Channel check failed: {exc}") from exc
        finally:
            if stream is not None:
                try:
                    stream.abort()
                finally:
                    stream.close()
