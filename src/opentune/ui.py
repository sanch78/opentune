"""Small routing experiment UI. No acoustic analysis or correction claims."""

from threading import Event

from PySide6.QtCore import Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QVBoxLayout, QWidget,
)

from opentune.audio import PortAudio
from opentune.signals import CHECK_LEVELS, CHECK_RATES


class Task(QThread):
    result = Signal(object)
    failed = Signal(str)

    def __init__(self, function, parent):
        super().__init__(parent)
        self.function = function

    def run(self):
        try:
            self.result.emit(self.function())
        except Exception as exc:
            self.failed.emit(str(exc))


class RoutingWindow(QMainWindow):
    def __init__(self, audio=None):
        super().__init__()
        self.audio = audio if audio is not None else PortAudio()
        self.task = None
        self.operation = ""
        self.cancel = Event()
        self.closing = False
        self.setWindowTitle("OpenTune — Channel check prototype")
        self.resize(780, 550)
        body = QWidget()
        layout = QVBoxLayout(body)
        intro = QLabel(
            "Your speakers. One sound.\n\n"
            "Start with your amplifier volume low. Select the output wired to it. "
            "Each button plays a short 500 Hz tone on one channel only. "
            "Digital level does not guarantee acoustic loudness."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.output = QComboBox()
        self.microphone = QComboBox()
        self.rate = QComboBox()
        for rate in CHECK_RATES:
            self.rate.addItem(f"{rate:,} Hz", rate)
        self.level = QComboBox()
        for level in CHECK_LEVELS:
            self.level.addItem(f"{level} dBFS peak", level)
        self.level.setCurrentIndex(2)
        form = QFormLayout()
        form.addRow("&Output device", self.output)
        form.addRow("&Microphone (discovery only)", self.microphone)
        form.addRow("Sample &rate", self.rate)
        form.addRow("Digital &level", self.level)
        layout.addLayout(form)
        self.refresh = QPushButton("&Refresh devices")
        self.probe = QPushButton("Check &format (silent)")
        row = QHBoxLayout()
        row.addWidget(self.refresh)
        row.addWidget(self.probe)
        layout.addLayout(row)
        self.armed = QCheckBox("My amplifier volume is low; enable the channel buttons")
        layout.addWidget(self.armed)
        self.left = QPushButton("Play &left")
        self.right = QPushButton("Play &right")
        self.stop = QPushButton("&Stop (Esc)")
        row = QHBoxLayout()
        for button in (self.left, self.right, self.stop):
            row.addWidget(button)
        layout.addLayout(row)
        self.status = QLabel("Discovering devices; no audio will play automatically.")
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setWordWrap(True)
        self.status.setAccessibleName("Routing status")
        layout.addWidget(self.status)
        limits = QLabel(
            "Windows: shared-mode WASAPI, stereo PCM only. Other platforms are experimental.\n"
            "Input is not recorded. A supported format is not proof of duplex measurement.\n"
            "Equalizer APO state is unknown. This check does not prove correction or complete Gate A.\n"
            "If a tone comes from both speakers or the wrong side, stop and check your routing.\n"
            "Restart after reconnecting devices; Refresh may read a cached device list."
        )
        limits.setWordWrap(True)
        layout.addWidget(limits)
        layout.addStretch()
        self.setCentralWidget(body)
        self.refresh.clicked.connect(self.discover)
        self.probe.clicked.connect(self.check_format)
        self.left.clicked.connect(lambda: self.play("left"))
        self.right.clicked.connect(lambda: self.play("right"))
        self.stop.clicked.connect(self.cancel_playback)
        self.escape = QShortcut(QKeySequence("Esc"), self)
        self.escape.activated.connect(self.cancel_playback)
        self.armed.toggled.connect(self.update_controls)
        for combo in (self.output, self.microphone, self.rate, self.level):
            combo.currentIndexChanged.connect(self.selection_changed)
        self.update_controls()
        QTimer.singleShot(0, self.discover)

    @Slot()
    def update_controls(self):
        busy = self.task is not None
        available = self.output.currentData() is not None
        for widget in (self.output, self.microphone, self.rate, self.level, self.refresh):
            widget.setEnabled(not busy)
        self.probe.setEnabled(not busy and available)
        self.armed.setEnabled(not busy and available)
        for button in (self.left, self.right):
            button.setEnabled(not busy and available and self.armed.isChecked())
        self.stop.setEnabled(busy and self.operation == "play")

    @Slot()
    def selection_changed(self):
        self.armed.setChecked(False)
        self.status.setText("Selection changed. Check the format and confirm amplifier volume before playback.")
        self.update_controls()

    def start_task(self, operation, function, message):
        if self.task is not None:
            return
        self.operation = operation
        self.cancel = Event()
        self.status.setText(message)
        self.task = Task(function, self)
        self.task.result.connect(self.task_result)
        self.task.failed.connect(self.task_failed)
        self.task.finished.connect(self.task_finished)
        self.update_controls()
        self.task.start()

    @Slot()
    def discover(self):
        if self.task is not None:
            return
        self.armed.setChecked(False)
        # A refresh deliberately discards transient IDs and prior selections.
        self.output.clear()
        self.microphone.clear()
        self.start_task("discover", self.audio.discover, "Discovering devices; no audio playback or recording.")

    @Slot()
    def check_format(self):
        output, mic, rate = self.output.currentData(), self.microphone.currentData(), self.rate.currentData()
        if output is None:
            return
        self.start_task("probe", lambda: self.audio.probe(output, mic, rate), "Checking formats without playing or recording.")

    def play(self, channel):
        if not self.armed.isChecked() or self.output.currentData() is None or self.task is not None:
            return
        output, rate, level = self.output.currentData(), self.rate.currentData(), self.level.currentData()
        self.start_task("play", lambda: self.audio.play_channel(output, rate, channel, level, self.cancel),
                        f"Checking {channel} at {level} dBFS peak. Stop immediately if routing is wrong.")

    @Slot()
    def cancel_playback(self):
        if self.task is not None and self.operation == "play":
            self.cancel.set()
            self.status.setText("Stopping channel check…")

    @Slot(object)
    def task_result(self, result):
        if self.operation == "discover":
            self.output.addItem("Select an output…", None)
            self.microphone.addItem("No microphone selected", None)
            for device in result:
                if device.outputs >= 2 and (self.audio.platform != "win32" or device.host_name == "Windows WASAPI"):
                    self.output.addItem(device.label, device)
                if device.inputs:
                    self.microphone.addItem(device.label, device)
            if self.output.count() == 1:
                self.status.setText("No eligible stereo output found. Check the connection and restart OpenTune.")
            else:
                self.status.setText(
                    f"Found {len(result)} endpoints across host APIs. Select the output explicitly. "
                    "Windows output choices are limited to stereo-capable WASAPI devices."
                )
        elif self.operation == "probe":
            self.status.setText(f"Stereo output format supported at {result.rate:,} Hz. {result.input_status}")
        else:
            self.armed.setChecked(False)
            if result.cancelled:
                self.status.setText("Channel check stopped. No routing or system settings were changed.")
            else:
                self.status.setText(
                    f"Tone finished ({result.rate:,.0f} Hz; reported output latency {result.latency * 1000:.0f} ms). "
                    "Confirm the intended speaker was heard. This is not correction verification."
                )

    @Slot(str)
    def task_failed(self, message):
        self.armed.setChecked(False)
        self.status.setText(f"Unable to continue: {message}")

    @Slot()
    def task_finished(self):
        self.task.deleteLater()
        self.task = None
        self.update_controls()
        if self.closing:
            self.close()

    def closeEvent(self, event):
        if self.task is not None:
            self.closing = True
            self.cancel_playback()
            event.ignore()
        else:
            event.accept()
