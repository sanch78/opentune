import numpy as np
import pytest

from opentune.signals import CHECK_LEVELS, CHECK_RATES, CHECK_SECONDS, channel_tone


@pytest.mark.parametrize("rate", CHECK_RATES)
@pytest.mark.parametrize("level", CHECK_LEVELS)
@pytest.mark.parametrize("channel,column", [("left", 0), ("right", 1)])
def test_bounded_ramped_channel_isolation(rate, level, channel, column):
    signal = channel_tone(channel, rate, level)
    assert signal.shape == (round(rate * CHECK_SECONDS), 2)
    assert signal.dtype == np.float32 and signal.flags.c_contiguous
    assert np.isfinite(signal).all()
    assert np.count_nonzero(signal[:, 1 - column]) == 0
    assert np.max(np.abs(signal)) <= 10 ** (level / 20) + 1e-9
    assert np.max(np.abs(signal)) > 0
    assert np.array_equal(signal[0], [0, 0])
    assert np.array_equal(signal[-1], [0, 0])
    # Startup is attenuated by the ramp, rather than jumping to a full sine.
    assert np.max(np.abs(signal[:round(rate * 0.005)])) < 0.03 * 10 ** (level / 20)


@pytest.mark.parametrize("channel,rate,level", [
    ("both", 48000, -48), ("left", 0, -48), ("right", 192000, -48),
    ("left", 48000, 0), ("left", 48000, float("nan")),
])
def test_rejects_unsafe_or_unsupported_signal_requests(channel, rate, level):
    with pytest.raises(ValueError):
        channel_tone(channel, rate, level)
