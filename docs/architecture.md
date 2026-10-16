# Architecture

Status: accepted direction, before implementation. See [ADR 0001](decisions/0001-initial-architecture.md).

## Product boundary

OpenTune matches repeatable left/right response differences at the listening
position. Measurements include the room, placement, playback chain, and microphone.
The first release cannot isolate a speaker's intrinsic response or diagnose and
repair physical loudspeaker defects.

Windows is the first functional release target. Linux is a first-class design
target. macOS remains **Community Testing Required** until physical testing.
Advanced room correction must not delay matching.

## Chosen technology

Python orchestrates workflows and offline analysis; NumPy/SciPy provide numerical
primitives. PySide6/Qt Widgets provides the GUI. sounddevice/PortAudio is the
initial measurement I/O candidate, subject to mixed-device validation. Equalizer
APO performs Windows endpoint correction. Python is not the planned always-on
system-wide real-time processing engine.

C++/Qt would offer tighter native control at a higher initial implementation cost.
Rust remains an option for a future processing service. Neither is necessary
before validating the measurement method. JUCE is not the default because its
AGPL/commercial licensing does not fit the intended dependency approach as well.
See [upstream references](references.md).

## Module boundaries

These are planned responsibilities, not existing packages or public APIs.

| Module | Owns | Must not own |
| --- | --- | --- |
| Measurement | Signals, synchronization, response estimation, quality flags | GUI, system configuration |
| Matching/DSP | Reliable response comparison, filter fitting, headroom analysis | Device discovery, backend activation |
| Microphones | Identity, calibration imports, provenance, usable bands | Invented model compensation |
| Audio devices | Capabilities, format negotiation, channel mapping, stream lifecycle | Acoustic target selection |
| Platform adapters | Endpoint identity, backend export/activation/bypass/restore | Measurement algorithms |
| Persistence | Versioned sessions, recordings, profiles, migrations | Silent recomputation or activation |
| Application | Workflow state, cancellation, progress, orchestration | Numerical algorithms |
| GUI | Accessible guidance, plots, controls | Direct audio callback work |
| Diagnostics | Local structured events, explicit diagnostic export | Default telemetry |

Dependencies flow from GUI to application services to core interfaces. Platform
adapters implement those interfaces; core algorithms never import platform APIs
or PySide6. Analysis operates on saved data as well as new captures.

## Interface responsibilities

- Audio I/O enumerates endpoints, validates a requested format, opens capture and
  playback, reports timing/dropouts, cancels, and closes resources.
- Measurement consumes a capture plus its stimulus/settings and produces immutable
  analysis results with quality evidence and algorithm version.
- Matching consumes channel analyses and explicit limits and returns a proposed
  profile plus predicted response and reasons for excluded regions.
- A correction backend reports capabilities and supports validation, export,
  activation, status inspection, bypass, and restoration where available.
- Persistence validates schemas and references without activating imported data.

Adapter capability flags must distinguish export-only support from activation,
status inspection, and verified processing. Unsupported operations return explicit
results rather than silently succeeding.

## Execution and failure handling

The GUI remains on its main thread. A worker handles acquisition and analysis;
audio callbacks only exchange preallocated buffers and minimal status. No GUI,
logging, file I/O, or optimization runs in callbacks. Python callback viability
must be measured; use a native buffer bridge if necessary.

The workflow progresses through device selection, route check, level check,
capture, quality review, analysis, proposal, activation, and verification. Each
transition can fail or be cancelled. Invalid capture never advances to automatic
correction. Device loss stops output and invalidates the session's live route.

Measurement requires an explicitly known correction state to prevent fitting an
already corrected response. Restore the previous state on cancellation/failure
and report any restoration failure visibly. Never switch to an unrelated output
automatically. Backend activation uses a staged, validated configuration and a
recoverable prior configuration.

## Data model and reproducibility

| Record | Essential content |
| --- | --- |
| Session | Schema/app versions, timestamps, route, device/backend identity, settings |
| Capture | Original WAV, channel, actual rate, stimulus parameters/hash, timing/dropouts |
| Analysis | Capture references, calibration hash/orientation, response, smoothing, confidence evidence |
| Profile | Source analyses, independent channel filters, shared attenuation, limits, algorithm version |
| Verification | Fresh captures, active backend/configuration identity, comparison results |

Use versioned JSON metadata and lossless WAV recordings. Preserve originals;
store derived analysis separately. Save calibration content or a stable copy and
hash, not only a path that may change. Validate finite values, channel counts,
filter stability, bounded sizes, and supported schema versions on import. Reject
unknown future schemas explicitly. No executable content in profile files.

Persist portable filter parameters (type, frequency, gain, Q), not only
sample-rate-specific coefficients or machine-specific backend configuration.
Device indices are transient; resolve saved identities and require confirmation
when ambiguous. Public exports omit private endpoint identifiers by default.

## Nonfunctional requirements

Corrections are reversible, confidence is evidence-based rather than a fabricated
accuracy percentage, and beginner guidance remains separate from advanced detail.
Provide keyboard operation, readable contrast, labeled graphs, and non-color-only
channel identification. All logging stays local unless the user exports it.
No hardware compatibility claims follow from a successful build alone.
