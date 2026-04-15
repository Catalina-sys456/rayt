from .tui import Rayt
import os
import sys


def check_root():
    if os.geteuid() != 0:
        print("Error: This program must be run as root.")
        sys.exit(1)


def main() -> None:
    check_root()
    app = Rayt()
    app.run()
