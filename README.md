# OpenTune

**Your speakers. One sound.**

OpenTune is a community-driven project for speaker measurement, matching, and,
eventually, room correction. Good sound should be accessible without expensive
proprietary software or mandatory professional measurement equipment.

## Project status

**Architecture and repository preparation. No application is available yet.**

The first release will focus on reducing repeatable left/right response
differences at the listening position. It will not identify the intrinsic
loudspeaker response independently of the room or promise professional accuracy
from an uncalibrated microphone.

The agreed stack is Python, PySide6, NumPy/SciPy, and sounddevice/PortAudio.
Windows correction will use an explicit Equalizer APO integration. These are
design decisions; hardware compatibility has not yet been demonstrated.

## Planned first experience

1. Select the output connected to your amplifier and your microphone input.
2. Follow microphone positioning and quiet channel-identification guidance.
3. Measure each speaker repeatedly with the microphone fixed in place.
4. Review measurement quality and conservative matching corrections.
5. Enable a reversible profile and take a fresh verification measurement.

No subscriptions, advertising, or telemetry by default are planned. GitHub is the
project home; no standalone website is planned.

## Platform scope

| Platform | Planned scope | Current validation |
| --- | --- | --- |
| Windows | First measurement and matching MVP; Equalizer APO | Not hardware tested |
| Linux | First-class target; PipeWire correction adapter | Not implemented or hardware tested |
| macOS | Portable core and future native integration | Community Testing Required |

System-wide correction depends on the selected endpoint and audio route. The
initial Windows scope is tested shared-mode stereo PCM playback. Exclusive
playback, ASIO, and encoded passthrough are outside that initial promise.

## Project documents

- [Architecture](docs/architecture.md)
- [Accepted decisions](docs/decisions/0001-initial-architecture.md)
- [Measurement and matching design](docs/measurement.md)
- [Platform integration](docs/platforms.md)
- [Feasibility gates and roadmap](docs/roadmap.md)
- [Validation strategy](docs/testing.md)
- [Development setup](docs/development.md)
- [Release and dependency strategy](docs/releases.md)
- [Upstream references](docs/references.md)

## Contributing

Contributions in acoustics, DSP, hardware compatibility, platform integration,
accessibility, translations, and usability are welcome. Read
[CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).
Public code, documentation, and initial UI text use English.

Repository checks currently validate documentation links and GitHub YAML, not
application behavior or audio compatibility. See the development guide to run them.

## License

OpenTune-authored code and documentation are available under the [MIT License](LICENSE).
Third-party dependencies retain their own licenses. In particular, choosing
PySide6 does not relicense Qt under MIT.
