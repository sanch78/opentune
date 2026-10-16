"""Run the GUI, or enumerate devices without playing/recording audio."""

import argparse
from dataclasses import asdict
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenTune routing prototype")
    parser.add_argument("command", nargs="?", choices=("devices",))
    args = parser.parse_args()
    if args.command == "devices":
        from opentune.audio import AudioError, PortAudio

        try:
            print(json.dumps([asdict(device) for device in PortAudio().discover()], indent=2))
        except AudioError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return 0
    from PySide6.QtWidgets import QApplication
    from opentune.ui import RoutingWindow

    app = QApplication(sys.argv[:1])
    window = RoutingWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
