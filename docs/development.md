# Development environment

## Current scope

Phase 2 starts with device discovery, silent format probing, and opt-in left/right
identification tones. No sweep capture, microphone recording, correction, or
installer exists yet. Read the [manual experiment guide](prototype.md).

## Prerequisites

- Git.
- Python 3.12 with `venv` and pip (initial compatibility baseline).
- A text editor; UTF-8 and LF are configured in `.editorconfig`/`.gitattributes`.

The initial GUI uses PySide6-Essentials (Qt Widgets); no Qt Addons or plotting
package is required. SciPy is deferred until response estimation needs it.

### Windows PowerShell

```powershell
git clone https://github.com/sanch78/opentune.git
cd opentune
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-runtime.txt -r requirements-dev.txt -e .
.\.venv\Scripts\python.exe tools/check_repository.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m opentune devices
.\.venv\Scripts\python.exe -m opentune
```

### Linux and macOS

```sh
git clone https://github.com/sanch78/opentune.git
cd opentune
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-runtime.txt -r requirements-dev.txt -e .
.venv/bin/python tools/check_repository.py
.venv/bin/python -m pytest -q
.venv/bin/python -m opentune devices
.venv/bin/python -m opentune
```

Activation is optional; the commands select the environment directly. Do not
commit `.venv`. For documentation-only edits, install `requirements-dev.txt` and run
the repository checker without installing the app. Full tests need the app/runtime.

## Runtime and platform constraints

`pyproject.toml` pins direct runtime dependencies; `requirements-runtime.txt` also
pins their transitive Python dependencies. Update both intentionally and verify
all target OS wheel sets. Python 3.12 is tested; 3.13/3.14 are within the package
constraints but not validated here. See [dependency inventory](dependencies.md).

Windows hardware validation starts with WASAPI shared mode. Linux needs native
libraries, for example `sudo apt-get install libportaudio2 libegl1 libopengl0` on
Debian/Ubuntu. Qt's pinned Linux x64 wheels require glibc 2.34 or later and its macOS
wheels require macOS 13 or later. macOS remains **Community Testing Required**.
Wheel availability is not proof of audio compatibility. Tests need neither hardware
nor Equalizer APO. Do not use private sounddevice internals to refresh devices.

The installed `opentune` command is equivalent to `python -m opentune`. No command-line
playback option exists: tones require GUI selection and volume acknowledgment.
Device enumeration and format probing do not open streams.

Keep private recordings, profiles, and diagnostic exports under ignored
`local-data/`. Submit only explicitly licensed, sanitized test fixtures.

## Pull requests and CI

Run the repository checker and pytest before submitting changes. CI runs repository
checks and offscreen prototype tests on all three OS families. Every audio test
uses fake devices; CI never plays or records sound and is not acoustic validation.
Read [CONTRIBUTING.md](../CONTRIBUTING.md) and use the PR template. Packaging jobs
added later must run real work; do not add empty installers.
