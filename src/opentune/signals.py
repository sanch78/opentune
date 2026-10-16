"""Bounded channel identification signal; not a measurement sweep."""

import numpy as np


CHECK_LEVELS = (-60, -54, -48, -42)
CHECK_RATES = (48000, 44100)
CHECK_SECONDS = 0.75


def channel_tone(channel: str, sample_rate: int, level_dbfs: int = -48) -> np.ndarray:
    """Return a ramped 500 Hz stereo tone with the other channel exactly silent.

    Levels are digital peak dBFS, not sound pressure. No caller can request a
    louder tone or an unbounded duration through this prototype interface.
    """
    if channel not in ("left", "right"):
        raise ValueError("Choose left or right.")
    if sample_rate not in CHECK_RATES or level_dbfs not in CHECK_LEVELS:
        raise ValueError("Unsupported channel-check rate or level.")
    count = round(sample_rate * CHECK_SECONDS)
    ramp = round(sample_rate * 0.05)
    envelope = np.ones(count)
    fade = np.sin(np.linspace(0, np.pi / 2, ramp)) ** 2
    envelope[:ramp] = fade
    envelope[-ramp:] = fade[::-1]
    tone = np.sin(2 * np.pi * 500 * np.arange(count) / sample_rate)
    data = np.zeros((count, 2), dtype=np.float32)
    data[:, 0 if channel == "left" else 1] = tone * envelope * 10 ** (level_dbfs / 20)
    return data
