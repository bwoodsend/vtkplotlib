# -*- coding: utf-8 -*-

import numpy as np
import sys
from vtkplotlib._get_vtk import vtk, QVTKRenderWindowInteractor

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from vtkplotlib.figures.BaseFigure import BaseFigure
from vtkplotlib import nuts_and_bolts
from vtkplotlib._vtk_errors import handler, silencer

if __name__ == "__main__":
    debug = print
else:
    debug = lambda *x: None


class QtFigure(BaseFigure, QWidget):
    """The VTK render window in a `PyQt5.QtWidgets.QWidget`.
    This can be embedded into a GUI the same way all other
    `PyQt5.QtWidgets.QWidget`\\ s are used.

    :param name: The window title of the figure, only applicable is **parent** is None, defaults to 'qt vtk figure'.
    :type name: str

    :param parent: Parent window, defaults to None.
    :type parent: :sip:class:`PyQt5.QtWidgets.QWidget`


    .. note::

        If you are new to Qt then this is a rather poor place to start. Whilst
        many libraries in Python are intuitive enough to be able to just dive
        straight in, Qt is not one of them. Preferably familiarise yourself
        with some basic Qt before coming here.


    This class inherits both from `PyQt5.QtWidgets.QWidget` and a
    vtkplotlib base figure class. Therefore it can be used exactly the same as
    you would normally use either a `PyQt5.QtWidgets.QWidget` or a
    `vtkplotlib.figure`.

    Care must be taken when using Qt to ensure you have **exactly one**
    `PyQt5.QtWidgets.QApplication`. To make this class quicker to use
    the qapp is created automatically but is wrapped in a

    .. code-block:: python

        if QApplication.instance() is None:
            self.qapp = QApplication(sys.argv)
        else:
            self.qapp = QApplication.instance()

    This prevents multiple `PyQt5.QtWidgets.QApplication` instances
    from being created (which causes an instant crash) whilst also preventing a
    `PyQt5.QtWidgets.QWidget` from being created without a qapp
    (which also causes a crash).


    On :func:`show()`, :sip:method:`qapp.exec_()
    <PyQt5.QtWidgets.QApplication.exec_>` is called automatically if
    ``figure.parent() is None`` (unless specified otherwise).

    If the figure is part of a larger window then ``larger_window.show()``
    must also explicitly show the figure. It won't begin interactive mode until
    `PyQt5.QtWidgets.QApplication.exec_` is called.


    If the figure is not to be part of a larger window then it behaves exactly
    like a regular figure. You just need to explicitly create it first.

    .. code-block:: python

        import vtkplotlib as vpl

        # Create the figure. This automatically sets itself as the current
        # working figure. The qapp is created automatically if one doesn't
        # already exist.
        vpl.QtFigure("Exciting Window Title")

        # Everything from here on should be exactly the same as normal.

        vpl.quick_test_plot()

        # Automatically calls ``qapp.exec_()``. If you don't want it to then
        # use ``vpl.show(False)``.
        vpl.show()


    However this isn't particularly helpful. A more realistic example would
    require the figure be part of a larger window. In this case, treat the
    figure as you would any other QWidget. You must explicitly call
    ``figure.show()`` however. (Not sure why.)

    .. code-block:: python

        import vtkplotlib as vpl
        from PyQt5 import QtWidgets
        import numpy as np
        import sys


        class FigureAndButton(QtWidgets.QWidget):
            def __init__(self):
                super().__init__()

                # Go for a vertical stack layout.
                vbox = QtWidgets.QVBoxLayout()
                self.setLayout(vbox)

                # Create the figure
                self.figure = vpl.QtFigure()

                # Create a button and attach a callback.
                self.button = QtWidgets.QPushButton("Make a Ball")
                self.button.released.connect(self.button_pressed_cb)

                # QtFigures are QWidgets and are added to layouts with `addWidget`
                vbox.addWidget(self.figure)
                vbox.addWidget(self.button)


            def button_pressed_cb(self):
                \"""Plot commands can be called in callbacks. The current working
                figure is still self.figure and will remain so until a new
                figure is created explicitly. So the ``fig=self.figure``
                arguments below aren't necessary but are recommended for
                larger, more complex scenarios.
                \"""

                # Randomly place a ball.
                vpl.scatter(np.random.uniform(-30, 30, 3),
                            color=np.random.rand(3),
                            fig=self.figure)

                # Reposition the camera to better fit to the balls.
                vpl.reset_camera(self.figure)

                # Without this the figure will not redraw unless you click on it.
                self.figure.update()


            def show(self):
                # The order of these two are interchangeable.
                super().show()
                self.figure.show()


            def closeEvent(self, event):
                \"""This isn't essential. VTK, OpenGL, Qt and Python's garbage
                collect all get in the way of each other so that VTK can't
                clean up properly which causes an annoying VTK error window to
                pop up. Explicitly calling QtFigure's `closeEvent()` ensures
                everything gets deleted in the right order.
                \"""
                self.figure.closeEvent(event)




        qapp = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

        window = FigureAndButton()
        window.show()
        qapp.exec_()


    .. note::  `QtFigure`\\ s are not reshow-able if the figure has a parent.

    .. seealso:: `vtkplotlib.QtFigure2` is an extension of this to provide some standard GUI elements, ready-made.

    """

    def __init__(self, name="qt vtk figure", parent=None):

        self.qapp = QApplication.instance() or QApplication(sys.argv)
        QWidget.__init__(self, parent)
        BaseFigure.__init__(self, name)

        self.vl = QVBoxLayout()
        self.setLayout(self.vl)

        self._vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(self.vtkWidget)

        self.renWin
        self.iren

    def _re_init(self):
        debug("re init")
        name = self.window_name
        QWidget.__init__(self, self.parent())
        self.window_name = name
        self.setLayout(self.vl)
        self.setWindowTitle(self.window_name)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.insertWidget(self._vtkWidget_replace_index, self.vtkWidget)

        self.renWin, self.iren

    @property
    def vtkWidget(self):
        if not hasattr(self, "_vtkWidget"):
            self._re_init()
        return self._vtkWidget

    @vtkWidget.setter
    def vtkWidget(self, widget):
        self._vtkWidget = widget

    @vtkWidget.deleter
    def vtkWidget(self):
        if hasattr(self, "_vtkWidget"):
            del self._vtkWidget

    def _base_show_wrap(QWidget_show_name):
        """Wrap all the ``QWidget.show()``, ``QWidget.showMaximized()`` etc
        methods so they can all be used as expected. Just in case Qt has changed
        and some ``show...()`` methods aren't present, this defaults to just
        ``show()``.
        """

        QWidget_show = getattr(QWidget, QWidget_show_name, QWidget.show)

        def show(self, block=None):
            if not hasattr(self, "vtkWidget"):
                self._re_init()
            self._connect_renderer()

            QWidget_show(self)

            self.iren.Initialize()
            self.renWin.Render()
            self.iren.Start()

            if block is None:
                block = self.parent() is None
            if block:
                self._flush_stdout()
                self.qapp.exec_()
            BaseFigure.show(self, block)

        show.__name__ = QWidget_show.__name__
        try:
            show.__qualname__ = QWidget_show.__qualname__
        except (AttributeError, TypeError):
            pass

        return show

    show = _base_show_wrap("show")
    showMaximized = _base_show_wrap("showMaximized")
    showMinimized = _base_show_wrap("showMinimized")
    showFullScreen = _base_show_wrap("showFullScreen")
    showNormal = _base_show_wrap("showNormal")

    @nuts_and_bolts.init_when_called
    def renWin(self):
        if not hasattr(self, "vtkWidget"):
            self._re_init()
        renWin = self.vtkWidget.GetRenderWindow()
        return renWin

    @nuts_and_bolts.init_when_called
    def iren(self):
        iren = self.renWin.GetInteractor()
        iren.SetInteractorStyle(self.style)
        return iren

    def update(self):
        BaseFigure.update(self)
        QWidget.update(self)
        self.qapp.processEvents()

#    def close(self):
#        BaseFigure.close(self)
#        QWidget.close(self)
#        self._clean_up()

    def on_close(self):
        debug("cleaning up")
        if hasattr(self, "_renWin"):
            # These prevent error dialogs popping up.
            self._disconnect_renderer()
            self.renWin.MakeCurrent()
            self.renWin.Finalize()

        if hasattr(self, "_vtkWidget"):
            self._vtkWidget_replace_index = self.vl.indexOf(self.vtkWidget)
            self.vl.removeWidget(self.vtkWidget)


#        self.renderer.RemoveAllViewProps()

        del self.vtkWidget, self.iren, self.renWin

    def closeEvent(self, event):
        self.on_close()

    window_name = property(QWidget.windowTitle, QWidget.setWindowTitle)

    def __del__(self):
        try:
            self.renderer.RemoveAllViewProps()
        except (AttributeError, TypeError):
            # In Python2, RemoveAllViewProps is already None
            pass

    def _prep_for_screenshot(self, off_screen=False):
        BaseFigure._prep_for_screenshot(self, off_screen)
        if off_screen:
            print("Off screen rendering can't be done using QtFigures.")
        self.show(block=False)

    def close(self):
        QWidget.close(self)
        # closeEvent seems to be called anyway but call this just to be sure.
        self.on_close()
        BaseFigure.close(self)
