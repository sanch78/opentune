# Release and dependency strategy

## Current state

There is no application version or release artifact yet. Repository CI validates
documentation and infrastructure only. No packaging or publishing workflow runs.

## Proposed application packaging

Use PyInstaller one-folder builds initially for inspectability and debugging.
Build on each target OS; PyInstaller is not a cross-compiler. Validate on a clean
machine without developer tools or a preinstalled Python interpreter.

| Target | Initial artifact direction | Release requirement |
| --- | --- | --- |
| Windows x64 | Versioned ZIP, then installer if justified | Physical audio-route and rollback testing |
| Linux x64 | Versioned archive, distribution format after compatibility study | Tested native-library baseline and PipeWire routing |
| macOS | Architecture-specific app bundle/archive | Community Testing Required; signing/notarization plan |

Choose final minimum OS versions and CPU architectures from actual dependency
support and hardware tests. Do not invent compatibility guarantees now. macOS
Intel/Apple Silicon coverage depends on available builders and contributors.

## Release process once the MVP exists

1. Run core tests, adapter tests, repository checks, and dependency/license review.
2. Build on native GitHub Actions runners with pinned tooling and bounded permissions.
3. Complete documented hardware smoke tests and record tested versions/routes.
4. Review notices, configuration migration, bypass, uninstall, and rollback behavior.
5. Publish versioned artifacts with checksums, changelog, limitations, and provenance.

Release publishing will be a separate explicit workflow introduced with an actual
application. Decide signing credentials and maintenance responsibility before
claiming trusted installation. A successful build is not a hardware test.

## Licensing and external software

OpenTune-authored work is MIT. PySide6/Qt, numerical libraries, audio libraries,
packaging tools, and external processors keep their own terms. Record versions,
licenses, source locations, modifications, and required notices in a dependency
inventory before distributing binaries. Review the actual transitive bundle.

Use LGPL-available Qt modules and a distribution layout that meets applicable
replacement/relinking and notice obligations; do not assume all Qt modules share
one license. Do not copy GPL/AGPL processor code into MIT modules. Assess any
proposed combined distribution separately.

Initially document Equalizer APO as a separately installed dependency. Do not
silently bundle its installer, change its license, or overwrite user settings.
Apply the same review to BlackHole or CamillaDSP before distributing them.

## Repository administration

After the initial push, use `main` as the default branch. When CI has run, configure
branch protection/rulesets with the repository check as required, subject to the
account's available features. GitHub-hosted settings, signing secrets, private
conduct-reporting contact, and security-reporting facilities require separate
administrative setup; files alone do not configure them.
