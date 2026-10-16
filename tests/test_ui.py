import time

import pytest
from PySide6.QtWidgets import QApplication

from opentune.audio import Device, PlaybackResult, RouteProbe
from opentune.ui import RoutingWindow


class FakeAudio:
    platform = "win32"

    def __init__(self):
        self.plays = []
        self.hold = False
        self.output = Device(0, "Test HDMI", 0, "Windows WASAPI", 0, 2, 48000)

    def discover(self):
        return (self.output, Device(1, "Legacy output", 1, "MME", 0, 2, 44100))

    def probe(self, output, mic, rate):
        return RouteProbe(rate, "No input capture tested.")

    def play_channel(self, output, rate, channel, level, cancel):
        self.plays.append((output, channel, level))
        if self.hold:
            cancel.wait(2)
        return PlaybackResult(cancel.is_set(), rate, 0.05)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def wait_until(app, predicate):
    deadline = time.monotonic() + 3
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    assert predicate()


@pytest.fixture
def window(app):
    audio = FakeAudio()
    widget = RoutingWindow(audio)
    widget.show()
    wait_until(app, lambda: widget.output.count() > 0 and widget.task is None)
    yield widget, audio
    widget.close()
    wait_until(app, lambda: widget.task is None)
    widget.close()


def test_initial_discovery_cannot_autoplay_and_windows_filters_outputs(window):
    widget, audio = window
    assert not audio.plays
    assert widget.output.count() == 2  # placeholder and WASAPI, not MME
    assert widget.output.currentData() is None
    assert not widget.left.isEnabled() and not widget.right.isEnabled()
    widget.play("left")
    assert not audio.plays


def test_play_requires_explicit_device_and_volume_acknowledgment(window, app):
    widget, audio = window
    widget.output.setCurrentIndex(1)
    assert not widget.left.isEnabled()
    widget.armed.setChecked(True)
    widget.right.click()
    wait_until(app, lambda: widget.task is None)
    assert len(audio.plays) == 1 and audio.plays[0][1:] == ("right", -48)
    assert not widget.armed.isChecked() and not widget.left.isEnabled()


def test_selection_change_invalidates_acknowledgment(window):
    widget, _ = window
    widget.output.setCurrentIndex(1)
    widget.armed.setChecked(True)
    widget.level.setCurrentIndex(0)
    assert not widget.armed.isChecked()


def test_format_check_and_refresh_never_play_and_refresh_discards_selection(window, app):
    widget, audio = window
    widget.output.setCurrentIndex(1)
    widget.probe.click()
    wait_until(app, lambda: widget.task is None)
    assert "format supported" in widget.status.text()
    widget.armed.setChecked(True)
    widget.refresh.click()
    wait_until(app, lambda: widget.task is None)
    assert widget.output.currentData() is None and not widget.armed.isChecked()
    assert not audio.plays


def test_playback_error_disarms_controls_and_explains_failure(window, app):
    widget, audio = window

    def fail(*args):
        raise RuntimeError("output disconnected")

    audio.play_channel = fail
    widget.output.setCurrentIndex(1)
    widget.armed.setChecked(True)
    widget.left.click()
    wait_until(app, lambda: widget.task is None)
    assert "output disconnected" in widget.status.text()
    assert not widget.armed.isChecked() and not widget.left.isEnabled()


def test_stop_and_close_cancel_without_blocking_gui(window, app):
    widget, audio = window
    audio.hold = True
    widget.output.setCurrentIndex(1)
    widget.armed.setChecked(True)
    widget.left.click()
    wait_until(app, lambda: len(audio.plays) == 1)
    assert widget.stop.isEnabled() and not widget.refresh.isEnabled()
    assert not widget.output.isEnabled()
    widget.stop.click()
    wait_until(app, lambda: widget.task is None)
    assert "stopped" in widget.status.text()
    widget.armed.setChecked(True)
    widget.left.click()
    wait_until(app, lambda: len(audio.plays) == 2)
    widget.close()
    wait_until(app, lambda: widget.task is None and not widget.isVisible())
