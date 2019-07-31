# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 18:59:14 2019

@author: Brénainn
"""


from .figures import (Figure as figure,
                      QtFigure,
                      gcf,
                      show,
                      view,
                      reset_camera,
                      save_fig,
                      close,
                      )
from .fancy_figure import QtFigure2
from .Arrow import arrow, quiver
from .Lines import Lines as plot
from .MeshPlot import MeshPlot as mesh_plot
from .Polygon import Polygon as polygon
from .ScalarBar import ScalarBar as scalar_bar
from .Scatter import scatter, Cursor as cursor
from .Text import Text as text
from .Text3D import Text3D as text3d

