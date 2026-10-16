# Windows routing prototype: first Phase 2 slice

## Implemented boundary

Device discovery, explicit output/input selection, silent format checks, and
separate opt-in left/right tones. This starts Gate A; it does not complete it.
There is no microphone recording, sweep, Equalizer APO integration, correction,
profile activation, or change to system routing/volume.

The GUI is a small experiment harness, not the final measurement wizard. Start it
with `python -m opentune`; use `python -m opentune devices` for JSON discovery only.
See [development setup](development.md) for installation.

## Playback policy

- Choose a stereo-capable output explicitly; no default output is preselected.
- Windows output choices use Windows WASAPI shared mode. No exclusive playback,
  automatic format conversion, or fallback endpoint is requested.
- Choose 48,000 or 44,100 Hz. Unsupported rates fail rather than silently changing.
- Each button emits a 500 Hz sine for 0.75 seconds, with 50 ms onset/offset ramps.
  The other digital channel is exactly silent.
- The default is -48 dBFS peak; choices are -60, -54, -48, and -42 dBFS. This is
  digital amplitude, not calibrated SPL. External amplifier gain is unknown.
- Before each tone, acknowledge that amplifier volume is low. Selection changes,
  errors, completion, cancellation, and refresh clear the acknowledgment.
- Stop/Esc requests abort; pending output buffers are discarded by the adapter.
  A worker keeps the GUI responsive. Driver/hardware latency still applies; this
  is not a guarantee of instantaneous acoustic silence.
- The adapter refuses reported output latency above 0.5 seconds, monitors completion,
  and treats stream status errors or premature completion as failed checks.

Formats are checked again immediately before opening the explicitly selected
output. A changed discovery snapshot is rejected. PortAudio's device list may be
cached and is not a stable OS endpoint registry. Refresh clears selection and
re-reads the list but cannot guarantee discovery of hotplug changes. Restart after
reconnect, display sleep, or device changes; native endpoint notifications and
stronger identity handling remain future work. No automatic rerouting is intended.

## Manual listening check

1. Stop other audio. Set the amplifier low and verify its physical speaker wiring.
2. Start OpenTune, select the HDMI monitor output explicitly, and leave 48,000 Hz
   initially. Select a microphone only if you want its format checked; it is not
   needed for this listening check.
3. Run **Check format (silent)**. It must report stereo output support. Input format
   support, if present, is separate from duplex capture or clock synchronization.
4. Acknowledge amplifier volume, then **Play left**. Confirm only the left speaker
   is heard. Stop/Esc if the route is wrong. Do not compensate for inaudibility by
   immediately turning the amplifier high.
5. Acknowledge again and **Play right**. Confirm only the right speaker is heard.
6. Try Stop during a tone; verify another tone needs acknowledgment again.
7. Note endpoint, selected/reported rate, reported latency, tone level, physical
   route, OS/backend versions, and your listening observations. Do not call a
   completed stream an audible verification without listening.

If both speakers sound on either check, inspect mono-audio settings, driver mixing,
and downstream wiring. The app cannot identify analog wiring from an HDMI name.
Do not alter system enhancements indiscriminately while planning to use an APO.

## Local evidence (2026-10-16)

- Windows enumeration succeeded with sounddevice 0.5.6 and its bundled PortAudio.
- A PA278QV/NVIDIA HDMI output was enumerated as stereo-capable WASAPI.
- Silent stereo float32 probes at 48,000 Hz succeeded for the HDMI output and a
  Realtek output. Both rejected 44,100 Hz without automatic conversion.
- No sound was emitted and no microphone was recorded during automated/local checks.
- Pytest validates bounded signals, isolation, failure cleanup, cancellation,
  explicit device selection, and GUI controls using fake audio devices.

These observations are not listening results, APO verification, or a completed
hardware compatibility report. No endpoint indices or private input names are
committed as fixtures. Real channel audibility and Stop latency still need testing.

## Remaining gates

Gate A still needs Equalizer APO independent channel processing, actual correction
and bypass verification, reconnect/display-sleep behavior, and restoration tests.
Gate B still needs the microphone model/input-chain assessment, actual capture,
synchronization, synthetic response recovery, and repeatable physical sweeps.
Do not begin acoustic correction claims based on this tone-only prototype.
