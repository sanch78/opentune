# Development environment

## Current scope

This repository contains architecture and infrastructure only. There is no app
entry point, Python package, audio output, or installer to run. Do not install
PySide6 or audio runtime dependencies just to edit the documentation.

## Prerequisites

- Git.
- Python 3.12 with `venv` and pip (initial compatibility baseline).
- A text editor; UTF-8 and LF are configured in `.editorconfig`/`.gitattributes`.

### Windows PowerShell

```powershell
git clone https://github.com/sanch78/opentune.git
cd opentune
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe tools/check_repository.py
```

### Linux and macOS

```sh
git clone https://github.com/sanch78/opentune.git
cd opentune
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python tools/check_repository.py
```

Activation is optional; the commands select the environment directly. PyYAML is
the only current third-party development requirement. Do not commit `.venv`.

## Future application environment

Before prototype implementation, select compatible pinned runtime versions for
Python, PySide6, NumPy/SciPy, sounddevice/PortAudio, and plotting. Add a `src` package,
`pyproject.toml`, and pytest only when real implementation exists. Preserve a
headless core and isolate OS dependencies. Validate available wheels on all three
platforms before locking the runtime set.

Windows measurement starts with a tested WASAPI device pair. Linux development
will need suitable native audio libraries and PipeWire. macOS will need microphone
permission and later a validated virtual route for correction. Do not require
hardware or Equalizer APO for core unit tests.

Keep private recordings, profiles, and diagnostic exports under ignored
`local-data/`. Submit only explicitly licensed, sanitized test fixtures.

## Pull requests and CI

Run the repository checker before submitting changes. CI repeats it on all target
OS families. Read [CONTRIBUTING.md](../CONTRIBUTING.md) and use the PR template.
Any CI application-test or packaging jobs added later must run real work; do not
add successful placeholder tests or empty installers.
