# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 21:02:41 2019

@author: Brénainn Woodsend


one line to give the program's name and a brief idea of what it does.
Copyright (C) 2019  Brénainn Woodsend

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
import os

import vtkplotlib as vpl
from unittest import TestCase, main, skipUnless


class TestFigures(TestCase):
    def test_figure_io(self):
        vpl.close()
        self.assertIs(vpl.gcf(False), None)
        
        vpl.set_auto_fig(False)
        self.assertIs(vpl.gcf(), None)
        
        fig = vpl.figure()
        self.assertIs(vpl.gcf(), None)
        del fig

        vpl.set_auto_fig()
        fig = vpl.gcf()
        self.assertTrue(fig is not None)
        
        self.assertIs(fig, vpl.gcf())
        vpl.close()
        self.assertIs(vpl.gcf(False), None)
        vpl.scf(fig)
        self.assertIs(fig, vpl.gcf())
        
        vpl.close()
        fig = vpl.figure()
        self.assertIs(fig, vpl.gcf())
        vpl.close()        
        
    
    def test(self):
        plots = vpl.scatter(np.random.uniform(-10, 10, (30, 3)))
        vpl.save_fig("im.jpg")
        os.remove("im.jpg")
        
        vpl.close()
        fig = vpl.figure() 
        for plot in plots:
            fig += plot
        vpl.show()
        
        
    def test_view(self):
        vpl.set_auto_fig(True)
        vpl.close()
        grads = np.array(vpl.geometry.orthogonal_bases(np.random.rand(3)))
        point = np.random.uniform(-10, 10, 3)
        vpl.quiver(np.broadcast_to(point, (3, 3)),
                   grads,
                   color=np.eye(3))
        
        vpl.view(focal_point=point,
                 camera_position=point-grads[0],
                 up_view=grads[1])
#        vpl.view(camera_direction=grads[0],
#                 up_view=grads[1],
#                 )
#        
        vpl.reset_camera()
#        vpl.view(point)
        
        
        vpl.text("Should be looking in the direction of the red arrow, with the green arrow pointing up")
        vpl.show()

        
    def test_multi_figures(self):
        vpl.close()
        
        vpl.set_auto_fig(False)
        
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
        
        vpl.set_auto_fig(True)
        
        
    @skipUnless(vpl.PyQt5_AVAILABLE, "PyQt5 not installed")
    def test_qfigure(self):
        fig = vpl.QtFigure("a qt widget figure")
        
        self.assertIs(fig, vpl.gcf())
    
        direction = np.array([1, 0, 0])
        vpl.quiver(np.array([0, 0, 0]), direction)
        vpl.view(camera_direction=direction)
        vpl.reset_camera()
    
        vpl.show()


    @skipUnless(vpl.PyQt5_AVAILABLE, "PyQt5 not installed")
    def test_qfigure2(self):
        fig = vpl.QtFigure2("a qt widget figure")
        self.assertIs(fig, vpl.gcf())
    
        vpl.scatter(np.arange(9).reshape((3, 3)).T)
        
        fig.add_all()
        
    
        vpl.show()



if __name__ == "__main__":
    
    main()  
    self = TestFigures()