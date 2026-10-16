# ADR 0001: Initial architecture and MVP boundary

- Date: 2026-10-16
- Status: Accepted by the project owner
- Scope: Architecture and infrastructure; not authorization to skip feasibility gates

## Context

OpenTune must remain free, community-maintainable, and cross-platform while
delivering useful relative matching on a Windows stereo setup first. The reference
route is HDMI to a monitor's analog output, then a conventional stereo amplifier.
Measurement reliability and actual system audio routing are the main unknowns.

## Decision

1. Use Python and PySide6 for application orchestration, analysis, and desktop UI.
2. Use Equalizer APO as an explicit Windows correction dependency.
3. Define the initial promise as matching at the listening position, not separating
   the loudspeaker's intrinsic response from room effects.

NumPy/SciPy and sounddevice/PortAudio are the initial supporting library choices.
Exact runtime versions will be locked after a compatibility experiment, before
application implementation. Python 3.12 is the initial development baseline.

## Consequences

- No custom Windows virtual audio driver or APO in the initial release.
- Installing OpenTune alone will not imply system-wide processing is ready.
- Acoustic analysis and profiles remain independent of Equalizer APO and Qt.
- Linux uses a future PipeWire adapter; macOS integration remains experimental.
- Python is not tasked with an always-running production audio processing loop.
- MIT applies to OpenTune-authored work; dependency license obligations remain.
- Relative matching still requires repeatability and microphone quality checks.

## Alternatives

C++/Qt/PortAudio is viable if acquisition constraints require native work. A full
C++ application is deferred to avoid premature complexity. Rust can support a
future native service. JUCE was considered but its licensing is less aligned with
the selected approach. A webview-based UI adds another runtime without resolving
the difficult audio-routing requirements.

## Revisit when

Revisit acquisition technology if mixed-device synchronization or callback
reliability fails validation. Revisit Windows integration if the reference HDMI
endpoint cannot reliably host Equalizer APO. Revisit the product promise only
with new measurement evidence and an explicit architecture decision.
