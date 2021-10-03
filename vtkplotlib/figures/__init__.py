# -*- coding: utf-8 -*-

from .figure import Figure
from .figure_manager import (
    gcf,
    scf,
    auto_figure,
    show,
    save_fig,
    screenshot_fig,
    close,
    reset_camera,
    view,
    zoom_to_contents,
)

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
    PyQt5_AVAILABLE = True
    del QtWidgets, QtCore, QtGui
except ImportError:
    PyQt5_AVAILABLE = False

if PyQt5_AVAILABLE:
    from .QtFigure import QtFigure
    from .QtGuiFigure import QtFigure2
