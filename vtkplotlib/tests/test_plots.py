# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 18:16:09 2019

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


from unittest import TestCase, main, skipUnless
import numpy as np

import vtkplotlib as vpl

try:
    from stl.mesh import Mesh
except ImportError:
    Mesh = None
    


class TestPlots(TestCase):
    def test_arrow(self):
        points = np.random.uniform(-10, 10, (2, 3))
        vpl.scatter(points)
        vpl.arrow(*points, color="g")
        vpl.show()
        
    
    def test_quiver(self):
        t = np.linspace(0, 2 * np.pi)
        points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
        grads = np.roll(points, 10)
        
        arrows = vpl.quiver(points, grads, color=grads)
        self.assertEqual(arrows.shape, t.shape)
        
        vpl.show()
        
    
    def test_plot(self):
        t = np.arange(0, 1, .1) * 2 * np.pi
        points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
        vpl.plot(points, color="r", line_width=3, join_ends=True)
        
        vpl.show()


    @skipUnless(Mesh, "numpy-stl is not installed")
    def test_mesh(self):
        import time
        
        fig = vpl.gcf()
        
        path = vpl.data.get_rabbit_stl()
        _mesh = Mesh.from_file(path)
        
        self = vpl.mesh_plot(_mesh.vectors)
        
    
        fig.show(False)
        
        t0 = time.time()
        for i in range(100):
    #        self.color = np.random.random(3)
    #        print(self.color)
            self.set_tri_scalars((_mesh.x[:, 0] + 3 * i) % 20 )
            _mesh.rotate(np.ones(3), .1, np.mean(_mesh.vectors, (0, 1)))
            fig.update()
            self.update_points()
    #        time.sleep(.01)
            if (time.time() - t0) > 1:
                break
        
        
        fig.show()
        
        
    def test_polygon(self):
        t = np.arange(0, 1, .1) * 2 * np.pi
        points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
        
        vpl.polygon(points, color="r")
        
        vpl.show()
    
    
    @skipUnless(Mesh, "numpy-stl is not installed")
    def test_scalar_bar(self):
        mesh = Mesh.from_file(vpl.data.get_rabbit_stl())
        plot = vpl.mesh_plot(mesh, scalars=mesh.x)
    
        vpl.scalar_bar(plot)
    
        vpl.show()


    def test_scatter(self):
        points = np.random.uniform(-10, 10, (30, 3))
    
        vpl.scatter(points,
                    color=points,
                    radius=np.abs(points[:, 0]) ** .5,
                    use_cursors=False
                    )[0]
            
        vpl.show()
        
        
    def test_text(self):
        vpl.text("text", (100, 100), color="g")
        vpl.show()
        

    def test_annotate(self):
        point = np.array([1, 2, 3])
        vpl.scatter(point)
        
        arrow, text = vpl.annotate(point, "A ball", np.array([0, 0, 1]))
        
        vpl.show()
        
    
    def test_surface(self):
        thi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 100),
                         np.linspace(0, np.pi, 50))


        x = np.cos(thi) * np.sin(theta)
        y = np.sin(thi) * np.sin(theta)
        z = np.cos(theta)
        
        vpl.Surface(x, y, z, color="g")
        vpl.show()



if __name__ == "__main__":
    
    main()
    
    self = TestPlots()
