# -*- coding: utf-8 -*-
"""Test the contents of the vtkplotlib.figures module."""

import time

import numpy as np
import os, sys
from pathlib import Path

import pytest
import vtkplotlib as vpl

from tests._common import checker, requires_interaction, TEST_DIR

from tests._common import VTKPLOTLIB_WINDOWLESS_TEST

pytestmark = pytest.mark.order(3)


def test_abstract():
    with pytest.raises(Exception):
        vpl.figures.BaseFigure.BaseFigure._abc_assert_no_abstract_methods()
    vpl.figure._abc_assert_no_abstract_methods()


def test_figure_io():
    vpl.close()
    assert vpl.gcf(False) is None

    vpl.auto_figure(False)
    assert vpl.gcf() is None

    with pytest.raises(vpl.figures.figure_manager.NoFigureError):
        vpl.screenshot_fig()

    fig = vpl.figure()
    assert vpl.gcf() is None
    del fig

    vpl.auto_figure(True)
    fig = vpl.gcf()
    assert fig is not None

    assert fig is vpl.gcf()
    vpl.close()
    assert vpl.gcf(False) is None
    vpl.scf(fig)
    assert fig is vpl.gcf()

    vpl.close()
    fig = vpl.figure()
    assert fig is vpl.gcf()
    vpl.close()


@checker()
def test_save():
    plots = vpl.scatter(np.random.uniform(-10, 10, (30, 3)))

    path = TEST_DIR / "name.png"

    if path.exists():
        os.remove(str(path))

    vpl.save_fig(path)
    assert path.exists()

    array = vpl.screenshot_fig(magnification=2)
    assert array.shape == tuple(i * 2 for i in vpl.gcf().render_size) + (3,)

    shape = tuple(i * j for (i, j) in zip(vpl.gcf().render_size, (2, 3)))
    vpl.screenshot_fig(pixels=shape).shape
    # The following will fail depending on VTK version
    # .assertEqual(vpl.screenshot_fig(pixels=shape).shape,
    #                  shape[::-1] + (3,))

    vpl.close()
    return array


def test_screenshot_then_show():
    """Verify that a screenshot followed by a show doesn't somehow lead to a
    segfault.
    """
    vpl.figure()
    vpl.quick_test_plot()
    vpl.screenshot_fig()
    vpl.show()


@checker()
def test_view():
    vpl.auto_figure(True)
    vpl.close()
    grads = np.array(vpl.geometry.orthogonal_bases(np.random.rand(3)))
    point = np.random.uniform(-10, 10, 3)
    vpl.quiver(np.broadcast_to(point, (3, 3)), grads, color=np.eye(3))

    vpl.view(focal_point=point, camera_position=point - grads[0],
             up_view=grads[1])
    vpl.reset_camera()

    vpl.text("Should be looking in the direction of the red arrow, "
             "with the green arrow pointing up")
    # Linux seems to need an extra prod to render this for some reason.
    vpl.show(block=False)


@requires_interaction
def test_multi_figures():
    vpl.close()

    vpl.auto_figure(False)

    plot = vpl.plot(np.random.uniform(-10, 10, (10, 3)), join_ends=True)
    figs = []
    for i in range(1, 4):
        fig = vpl.figure("figure {}".format(i))
        fig += plot
        vpl.view(camera_direction=np.random.uniform(-1, 1, 3), fig=fig)
        vpl.reset_camera(fig)

        fig.show(False)
        figs.append(fig)
    fig.show()

    vpl.auto_figure(True)


def test_add_remove():
    fig = vpl.figure()
    plots = vpl.quick_test_plot(None)
    fig += plots
    fig.show(False)
    fig -= plots
    for i in plots:
        fig += i
        fig.update()
        time.sleep(.02)
    for i in plots:
        fig -= i
        fig.update()
        time.sleep(.02)
    vpl.close(fig)


@checker()
def test_zoom():
    vpl.scatter(np.random.uniform(-20, 20, (30, 3)), color="r")
    vpl.show(block=False)
    balls_to_ignore = vpl.scatter(np.random.uniform(-50, 50, (30, 3)))
    vpl.text("This should be ignored by zoom.")
    vpl.zoom_to_contents(plots_to_exclude=balls_to_ignore)


if __name__ == "__main__":
    pytest.main([__file__])
