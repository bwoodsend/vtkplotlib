# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# vtkplotlib isn't zip safe and I have no intention of trying to make it so.
# Hence, using __file__ instead of (super slow) pkg_resources is fine.

from vtkplotlib import __file__ as _init_path

DATA_FOLDER = Path(_init_path).with_name("data")

MODELS_FOLDER = DATA_FOLDER / "models"


def get_rabbit_stl():
    return str(MODELS_FOLDER / "rabbit" / "rabbit.stl")


ICONS_FOLDER = DATA_FOLDER / "icons"
ICONS = {i.stem: str(i) for i in ICONS_FOLDER.glob("*.jpg")}

_HOOKS_DIR = DATA_FOLDER.with_name("__PyInstaller")


def _get_hooks_dir():
    return [str(_HOOKS_DIR)]


def assert_ok():
    assert ICONS_FOLDER.is_dir()
    assert MODELS_FOLDER.is_dir()
    assert Path(get_rabbit_stl()).exists()
    assert _HOOKS_DIR.exists()


if __name__ == "__main__":
    assert_ok()
