# Platform audio integration

All hardware and routing combinations below require testing. Upstream software
capabilities are documented in [references](references.md); they are not OpenTune
compatibility results.

## Measurement I/O

PortAudio is the first abstraction for capture/playback. Devices in a single
PortAudio stream must use the same host API; arbitrary cross-host device pairing
must not be assumed. Probe the selected input/output combination and actual sample
rate. Separate streams, if needed, require explicit timing and drift handling.
Preserve channel mapping and handle endpoint loss without redirecting output.

## Windows: Equalizer APO

Equalizer APO supports channel selection, parametric filters, and preamp settings.
The MVP targets tested shared-mode stereo PCM routes on selected endpoints.
Do not promise processing of exclusive mode, ASIO, encoded passthrough, or every
driver configuration. Normal WASAPI loopback captures a mix; it does not insert
filters into the output path.

Planned adapter behavior:

- Detect an existing installation and inspect capabilities without modifying it.
- Guide the user through endpoint setup using Equalizer APO's own tools.
- Generate an OpenTune-owned include file with independent left/right sections.
- Preserve unrelated configuration; never replace the user's complete setup.
- Record prior state, stage and validate updates, and restore only OpenTune changes.
- Make activation and bypass status visible; report permission/restart requirements.
- Require an audible/measurement verification of the selected route before marking
  processing verified. File presence alone is insufficient.

Do not silently install third-party software or bundle it before license review.
Normal analysis and UI should not require administrator privileges. Installation
and protected configuration changes may require a separate elevated step.

For the reference HDMI-to-monitor-to-amplifier route, test stereo channel order,
monitor volume behavior, driver enhancements, display sleep, reconnect, sample-rate
changes, and changed endpoint identity. OpenTune cannot infer the analog wiring
after the monitor from the HDMI endpoint name.

Before a raw measurement, ensure the active correction state is known and bypassed
or route explicitly around it. Do not indiscriminately disable all enhancements
while depending on the APO enhancement path for correction.

## Linux: PipeWire

Plan an OpenTune-managed filter sink using PipeWire filter-chain, with independent
channel EQ and a reversible route to the selected hardware sink. PipeWire documents
channel-specific parametric EQ. Validate default routing, application overrides,
WirePlumber/session behavior, device loss, rate changes, and restoration.

Avoid modifying unrelated system configuration. Document that applications routed
directly to another sink or bypassing PipeWire are outside the corrected route.
Keep Linux-specific management out of the measurement and matching core.

## macOS: Community Testing Required

CoreAudio I/O and a virtual route such as BlackHole are candidates. A processor
must consume the virtual device and render to the physical device; virtual routing
alone is not correction. Investigate clock drift, device aggregation, latency,
permissions, process recovery, signing/notarization, and third-party licenses.
Do not claim a tested backend or full compatibility based on CI builds.

CamillaDSP is a reusable IIR/FIR processor candidate, not an automatic solution to
system routing. Evaluate it before writing a native processor. Its source and
binary distribution obligations need separate review before integration.
