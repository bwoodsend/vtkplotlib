# -*- coding: utf-8 -*-
# =============================================================================
# Created on Thu Oct 31 18:33:44 2019
#
# @author: Brénainn Woodsend
#
#
# one line to give the program's name and a brief idea of what it does.
# Copyright (C) 2019  Brénainn Woodsend
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================
"""
"""


import numpy as np
import matplotlib.pylab as plt
import sys
import os
from pathlib2 import Path


import vtkplotlib as vpl

print(dir(vpl))


plots = \
"""scatter
plot
mesh_plot
mesh_plot_with_edge_scalars
polygon
scalar_bar
arrow
quiver
text
text3d
annotate
surface
PolyData
"""

figures = \
"""show
figure
gcf
scf
reset_camera
save_fig
view
close
figure_history
auto_figure
QtFigure
QtFigure2
"""

extras = \
"""zip_axes
unzip_axes
TextureMap
quick_test_plot
"""

submodules = {key: val.strip().split() for (key, val) in [("Plots", plots),
                                                          ("Figures", figures),
                                                           ("Extras", extras)]}

import types

for (title, functions) in submodules.items():
    with open(Path(__file__).with_name(title + ".rst"), "w") as f:
        line = "vtkplotlib {}".format(title)
        f.writelines((line, "\n", "=" * len(line), "\n\n\n"))

        for name in functions:
            line = "vtkplotlib." + name
            f.writelines((line, "\n", "-" * len(line), "\n\n.. auto"))

            function = getattr(vpl, name)
            if isinstance(function, type):
                line = "class"
            elif isinstance(function, types.FunctionType):
                line = "function"
            else:
                line = "data"
                function.__name__ = name

            f.writelines([line,
                          ":: ",
                          function.__module__,
                          ".",
                          function.__name__,
                          "\n\n\n",
                          ])

if __name__ == "__main__":
    pass
