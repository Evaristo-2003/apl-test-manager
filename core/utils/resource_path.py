#!/usr/bin/env python3

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """
    Compatible con Python normal y PyInstaller
    """

    if hasattr(
        sys,
        "_MEIPASS"
    ):
        base_path = Path(
            sys._MEIPASS
        )
    else:
        base_path = Path(
            __file__
        ).resolve().parents[2]

    return base_path / relative_path