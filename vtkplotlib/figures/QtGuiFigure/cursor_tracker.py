# -*- coding: utf-8 -*-
"""
"""

from vtkplotlib.interactive import pick, call_super_callback


class CursorTracker(object):

    def __init__(self, fig):
        self.fig = fig
        self.init_labels()
        self.fig.style.AddObserver("MouseMoveEvent", self.mouse_move_cb)
        self.set_no_cursor()

    def init_labels(self):
        from PyQt5 import QtWidgets
        self.text_labels = [QtWidgets.QLabel(i) for i in "Cursor X Y Z".split()]
        self.coord_labels = [QtWidgets.QLabel() for i in range(3)]

        # yapf:disable
        self.labels = [self.text_labels[0]]
        [self.labels.extend(i)
         for i in zip(self.text_labels[1:], self.coord_labels)]
        [label.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
         for label in self.coord_labels]
        # yapf:enable

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch()
        [layout.addWidget(i) for i in self.labels]

        self.fig.vl.addLayout(layout)

    def set_cursor_position(self, position):
        for (label, axis) in zip(self.coord_labels, position):
            label.setText(format(axis, "6.2f"))

    def set_no_cursor(self):
        for label in self.coord_labels:
            label.setText("  --  ")

    def mouse_move_cb(self, style, event_name):
        picker = pick(style)

        if picker.actor is None:
            self.set_no_cursor()
        else:
            self.set_cursor_position(picker.point)
        call_super_callback()


if __name__ == "__main__":
    import vtkplotlib as vpl

    fig = vpl.QtFigure2()
    style = fig.style

    tracker = CursorTracker(fig)
    balls = vpl.quick_test_plot()

    vpl.show()
