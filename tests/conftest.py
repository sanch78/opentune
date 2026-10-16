import os

# Tests never show a native window or require an audio device.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
