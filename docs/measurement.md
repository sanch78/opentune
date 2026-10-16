# Measurement and matching design

This is a proposed method, not an implemented or validated acoustic algorithm.

## Guided acquisition

1. Select the actual output and input, negotiate a supported common sample rate,
   and verify stereo PCM channel mapping with quiet identification signals.
2. Position the microphone at ear height at the listening position. Keep its
   position and orientation fixed across both channels and all repeats.
3. Record background noise and check input headroom. Disable AGC, noise suppression,
   echo cancellation, and unwanted processing where possible. If processing cannot
   be disabled or its behavior is uncertain, flag or reject measurement.
4. Begin with a quiet bounded signal and a gradual ramp. The user retains amplifier
   volume control; do not automatically increase level without an explicit bound.
5. Capture alternating left/right logarithmic sweeps with pre/post silence and
   repeated measurements. Start with at least two captures per channel; determine
   final sweep length and repeat count experimentally.
6. Estimate timing, response, noise, clipping, dropouts, and repeatability before
   proposing filters. Provide immediate cancellation throughout output.

Input/output latency and sample-clock drift are different problems. Initial
alignment alone is insufficient for independent devices. Evaluate acoustic timing
markers and validated drift correction. Prefer shorter captures or reject results
when synchronization cannot be established. Never fabricate phase accuracy.

Digital dBFS is not acoustic SPL. Unknown amplifier gain and microphone sensitivity
prevent a guaranteed acoustic level. Do not display calibrated SPL without a
traceable sensitivity reference. Quiet defaults reduce risk but cannot guarantee
safe sound pressure for arbitrary external gain.

## Microphone profiles

Store manufacturer/model, optional serial-specific calibration, provenance,
orientation, frequency units, compensation sign convention, valid frequency range,
and limitations. Parse calibration files defensively; the first supported format
should be documented frequency/level text data. Do not guess header semantics,
silently reverse compensation signs, or extrapolate beyond supported data.

An Audyssey profile may identify a model without providing compensation. Receiver
calibration is not automatically available on a PC. Verify connector wiring, bias
requirements, and input compatibility for the exact model before recommending an
adapter. Never assume that a 3.5 mm connector establishes electrical compatibility.

The same stable microphone chain can reduce common response bias in a relative
comparison. Directionality, different incidence angles, time-varying gain, and
noise remain limitations. Uncalibrated microphones receive conservative usable
bands and explicit uncertainty, not a claim of professional accuracy.

## Response analysis

Use established logarithmic-sweep deconvolution and impulse-response analysis.
Retain the raw capture, impulse response, window parameters, unsmoothed response,
smoothed response, and quality evidence. Evaluate fractional-octave smoothing and
frequency-dependent reliability. Short reflection-free windows limit low-frequency
resolution; do not present gated bass results as high-resolution speaker facts.

The listening-position response includes the room. Shared response features should
not be flattened merely because they deviate from a flat line. Stable differences
are candidates for matching, not proof of a loudspeaker defect. Nearby-position
checks are useful validation evidence even before a full multi-position mode.

## Conservative filter proposal

Compare reliable smoothed responses in dB and derive a shared shape that preserves
their common character. A candidate cut-only target can be lowered where necessary
to avoid boosts. Fit a few broad parametric filters with constrained optimization;
validate the complete resulting cascade rather than each filter in isolation.

Experimental starting policy:

| Parameter | Initial candidate |
| --- | --- |
| Gain | No positive filter gains |
| Attenuation | Up to about 6 dB; also constrain the total cascade |
| Filters | Three to six per channel |
| Correction band | Approximately 200 Hz to 8 kHz, narrowed by evidence |
| Bandwidth | Broad filters; numeric Q bounds to be chosen in validation |
| Invalid regions | No automatic correction |

These values are hypotheses, not published accuracy or safety guarantees. The
algorithm may return no correction. Do not equalize deep nulls, narrow unstable
features, missing bandwidth, or suspected physical defects. Defer phase inversion,
delay alignment, FIR phase correction, and full-band automatic equalization.

Use established biquad equations. Compute headroom for the aggregate response;
cut-only filters alone do not guarantee absence of transient overshoot. Test filter
stability and demanding waveforms, retain a conservative shared gain margin, and
validate backend coefficient behavior at each supported sample rate. Do not claim
true-peak protection without a verified implementation that provides it.

## Results and verification

Label uncorrected measurements, predicted corrections, and fresh corrected
measurements separately. Report improvement over reliable frequency regions with
repeatability evidence, not a single unexplained score. Use level-matched bypass
comparisons so loudness changes do not masquerade as improvement. A new measurement
must establish that the intended route was actually corrected.
