# Contributing to OpenTune

Thank you for helping make speaker calibration accessible.

## Before starting

Read the [architecture](docs/architecture.md), [roadmap](docs/roadmap.md), and
[accepted decisions](docs/decisions/0001-initial-architecture.md). Discuss major
architecture, algorithms, dependencies, and platform changes in an issue first.
The current milestone starts device discovery and channel checking; further
measurement and correction implementation follows the agreed feasibility gates.

## Workflow

1. Fork the repository or create a focused branch from `main`.
2. Follow the [development guide](docs/development.md).
3. Keep changes small and explain the user-visible problem and resulting behavior.
4. Run repository checks and any meaningful tests for the changed behavior.
5. Open a pull request using the supplied template.

Use readable English names and documented module boundaries. Put OS-specific
behavior behind adapters. Do not couple analysis to the GUI or imply that writing
a backend configuration proves audio processing is active.

## Acoustic and hardware contributions

Include hardware models, microphone/calibration provenance, OS and driver details,
sample rate, routing, algorithm version, and repeatability evidence. Separate
synthetic fixtures, actual recordings, predictions, and verification measurements.
Follow the [validation strategy](docs/testing.md).

Do not commit personal recordings or large datasets without agreement. Remove
device serial numbers and other identifying metadata from public reports. Only
submit fixtures you have permission to distribute, with provenance and a license.

## Dependencies and licensing

OpenTune-authored contributions use MIT. By submitting a contribution, you agree
to provide it under the repository license. Preserve third-party notices and
identify new dependency licenses in the pull request. Do not copy code from
incompatible projects or assume free software is MIT-licensed.

## Community

Follow the [Code of Conduct](CODE_OF_CONDUCT.md). Contributions to hardware
documentation, accessibility, usability, translations, and testing are valuable
alongside application code. Do not publish unverified acoustic performance claims.
