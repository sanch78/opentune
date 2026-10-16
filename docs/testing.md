# Validation strategy

## Current automated checks

`python tools/check_repository.py` checks required repository files, local Markdown
file links, UTF-8/text hygiene, YAML parsing, and essential workflow/issue-template
structure. It does not check external URLs, Markdown anchor targets, audio behavior,
or GitHub's complete server-side workflow schema. The CI matrix runs the same check
on Windows, Linux, and macOS with Python 3.12.

There are no application tests yet because there is no application. A successful
repository check is not evidence of DSP accuracy or platform compatibility.

## Tests required as implementation arrives

Use pytest for headless core tests, with deterministic generated signals and
documented tolerances. Add tests alongside the behavior they validate.

| Layer | Evidence required |
| --- | --- |
| Signals | Bounded levels, ramps, channel isolation, deterministic length |
| Estimation | Known responses, delays, noise levels, clock mismatch, invalid captures |
| Matching | Shared response preserved, stable differences reduced, nulls rejected |
| Filters | Stable poles, combined limits, rate behavior, peak/headroom stress tests |
| Persistence | Round trips, invalid/nonfinite data, future schemas, bounded imports |
| Adapters | Export response parity, state transitions, rollback, unrelated config preserved |
| Workflow | Cancellation, quality rejection, device loss, restoration failure |
| GUI | Keyboard navigation, readable status, correct measurement/prediction labels |

Compare exports against the internal frequency response at supported sample rates.
Keep algorithm tests independent of GUI/audio hardware. CI must not emit test audio
or pretend that hosted runners provide meaningful physical acoustic validation.

## Hardware protocol

1. Record OS, app/backend/driver versions, endpoint mapping, rate, and full route.
2. Record microphone model, input chain, calibration provenance, orientation, and
   placement. Keep original recordings locally with reproducible settings.
3. Run repeat captures and inspect noise, clipping, dropouts, timing, and gain drift.
4. Compare with an independent measurement application using equivalent settings.
5. Activate correction and take fresh captures on the verified route.
6. Assess the same position and nearby positions; record regressions as well as gains.
7. Test level-matched bypass, endpoint reconnect, application restart, and rollback.

Define acceptance tolerances before each experiment. Derive them from synthetic
accuracy and observed repeatability, not an arbitrary marketing target. Reports
must separate known results, interpretations, and unresolved assumptions.

Do not upload recordings containing private speech or identifying metadata without
explicit consent. Keep distributable fixtures small and include their license.
