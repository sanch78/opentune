# Prototype dependency inventory

This is a development inventory, not a completed binary-distribution license
audit. No application binaries or third-party installers are released.

| Dependency | Pin | Purpose | Upstream licensing reference |
| --- | --- | --- | --- |
| NumPy | 2.5.4 | Signal buffers and generation | [NumPy license](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |
| PySide6-Essentials | 6.10.3 | Qt Core/Gui/Widgets | [Qt for Python licenses](https://doc.qt.io/qtforpython-6/licenses.html) |
| shiboken6 | 6.10.3 | PySide6 binding runtime | [Qt for Python licenses](https://doc.qt.io/qtforpython-6/licenses.html) |
| sounddevice | 0.5.6 | PortAudio binding | [sounddevice license](https://github.com/spatialaudio/python-sounddevice/blob/master/LICENSE) |
| CFFI | 2.1.1 | Native binding dependency | [CFFI license](https://cffi.readthedocs.io/en/latest/) |
| pycparser | 3.11 | CFFI dependency | [pycparser](https://github.com/eliben/pycparser) |
| PyYAML | 6.0.3 | Repository validation | [PyYAML](https://pyyaml.org/wiki/PyYAML) |
| pytest | 9.1.1 | Development tests | [pytest license](https://docs.pytest.org/en/stable/license.html) |

Qt and PortAudio native components and their transitive libraries retain their
own notices. The Windows sounddevice wheel supplies PortAudio; Linux typically
uses a system library. Review actual bundled files before distribution and retain
all applicable notices. Using Essentials does not imply every bundled Qt tool is
LGPL; this prototype imports only Core, Gui, and Widgets.

Top-level runtime requirements are pinned in `pyproject.toml`; all selected Python
runtime dependencies are pinned in `requirements-runtime.txt`. Build tooling and
test transitive dependencies are not a hermetic, hash-locked toolchain yet.

## Compatibility evidence

PyPI release metadata was checked for all runtime pins on 2026-10-16. Compatible
Python 3.12 wheels are published for Windows x64, Linux x64, and macOS (Intel/Apple
Silicon via Qt universal2 and appropriate NumPy/CFFI wheels). Generic pure-Python
wheels cover sounddevice on Linux and pycparser across platforms.

The Qt 6.10.3 wheels set the initial distribution floors to glibc 2.34 for Linux
x64 and macOS 13. These are package constraints, not validated hardware support.
Windows installation and offscreen tests ran locally. Cross-platform CI validates
installation and fake-device tests only. No SciPy or plotting package is installed
until measurement analysis requires it.
