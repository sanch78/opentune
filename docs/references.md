# Upstream references

Reviewed for the initial architecture on 2026-10-16. Capabilities below are upstream
documentation claims, not tested OpenTune behavior. Recheck licenses and supported
versions when choosing the actual dependency lock.

| Source | Relevance |
| --- | --- |
| [Qt for Python](https://doc.qt.io/qtforpython-6/) | Official PySide6 bindings and desktop framework |
| [Qt licensing](https://doc.qt.io/qt-6/licensing.html) | Module-specific LGPL/GPL/commercial terms |
| [SciPy signal](https://docs.scipy.org/doc/scipy/reference/signal.html) | Established signal-processing primitives |
| [sounddevice](https://python-sounddevice.readthedocs.io/) | Python PortAudio bindings |
| [Stream constraints](https://python-sounddevice.readthedocs.io/en/latest/api/streams.html) | Callback timing and stream behavior |
| [PortAudio overview](https://portaudio.com/docs/v19-doxydocs-dev/api_overview.html) | Device/host API restrictions |
| [Equalizer APO configuration](https://sourceforge.net/p/equalizerapo/wiki/Configuration%20reference/) | Channel filters, preamp, includes |
| [WASAPI loopback](https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording) | Capture of rendered audio, not processing insertion |
| [PipeWire filter-chain](https://docs.pipewire.org/page_module_filter_chain.html) | Channel-specific parametric EQ |
| [BlackHole](https://github.com/ExistentialAudio/BlackHole) | Candidate macOS virtual audio route |
| [CamillaDSP](https://github.com/HEnquist/camilladsp) | Existing cross-platform IIR/FIR processor candidate |
| [REW measurements](https://www.roomeqwizard.com/betahelp/help/html/makingmeasurements.html) | Timing references and independent-clock limitations |
| [Denon microphone guidance](https://support-uk.denon.com/app/answers/detail/a_id/20305/~/audyssey-microphone) | Receiver-side microphone compensation |
| [Audio EQ Cookbook](https://www.w3.org/TR/audio-eq-cookbook/) | Established biquad coefficient definitions |
| [PyInstaller](https://www.pyinstaller.org/en/stable/) | Native-OS packaging requirements |
| [JUCE licensing](https://juce.com/get-juce/) | Alternative framework licensing tradeoff |

REW is a potential external validation tool, not a selected source-code dependency.
Availability at no cost does not establish permission to reuse source or redistribute.
