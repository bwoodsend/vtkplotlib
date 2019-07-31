# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 14:14:44 2019

@author: Brénainn Woodsend

plot_3d_vtk.py
Wrap up some VTK methods to create a simpler matplotlib style programming interface.
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

#!/usr/bin/env python



import vtk
import numpy as np
#from matplotlib import pylab as plt
from matplotlib import colors
import os
import sys
from pathlib2 import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )

import nuts_and_bolts
import geometry as geom




class Colors(object):
    BACKGROUND = (.7, .7, .7)#tuple(np.array([20, 50, 100]) / 256)
    MARKER = (0, 0, 0)
    HIGHLIGHTED = (1, 0, 0)
    
mpl_colors = {}
mpl_colors.update(colors.BASE_COLORS)
for dic in (colors.CSS4_COLORS, colors.TABLEAU_COLORS, colors.XKCD_COLORS):
    for (key, val) in dic.items():
        mpl_colors[key.split(":")[-1]] = colors.hex2color(val)
    



class VTKRenderer(object):
    def __init__(self, window=None, window_interactor=None):

        # Create a renderwindow
        # The render window can either be vtk's default window type or 
        # a special PyQt compatible one
        if window is None:
            self.renWin = vtk.vtkRenderWindow()
        else:
            self.renWin = window
        
        self.data_holder = []
    
        # Create a renderer
        self.render = vtk.vtkRenderer()
        # And add it to the render window
        self.renWin.AddRenderer(self.render)
        self.render.SetBackground(Colors.BACKGROUND)
        
        # Create a renderwindowinteractor
        # The render window interactor can either be vtk's default window type or 
        # a special PyQt compatible one
        if window_interactor is None:
            iren = vtk.vtkRenderWindowInteractor()
        else:
            iren = window_interactor
        iren.SetRenderWindow(self.renWin)
        iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        self.actors = []
#        self.paths = {}
        
        self.iren = iren
        self.window_name = ""
        
        
    def start(self):
        # Enable user interface interactor
        # This needs to happen after some of the Qt stuff is done
        self.iren.Initialize()
        self.renWin.Render()
        self.renWin.SetWindowName(self.window_name)
        self.iren.Start()
        


    def open_stl(self, key):
        stl_path = key[0]
        stl_path = Path(stl_path)

        global reader

        # Read the stl directly from file
        reader = vtk.vtkSTLReader()
        # VTK can't handle é in my paths. Having to use this work-around        
        folder, filename = os.path.split(stl_path)
        old_wd = os.getcwd()
        os.chdir(folder)
        reader.SetFileName(filename)
        
        global mapper
        global actor
        # create an actor for the stl
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
#        self.stl_actors[key] = actor
#        self.paths[key] = stl_path

        # Assign actor to the renderer  
        self.render.AddActor(actor)
#        self.renWin.Render()
        self.render.ResetCamera()
        os.chdir(old_wd)
#        self.set_color(key, next(colors_and_colormaps.color_loop))
        
        
    def set_color(self, key, color):
        self.stl_actors[key].GetProperty().SetColor(color[:3])
        if len(color) == 4:
            self.stl_actors[key].GetProperty().SetOpacity(color[3])
            
    def show_actor(self, key):
        self.stl_actors[key].SetVisibility(1)
        self.renWin.Render()
    
    def hide_actor(self, key):
        self.stl_actors[key].SetVisibility(0)
        self.renWin.Render()
        
    def close_stl(self, key):
        actor = self.stl_actors[key]
        self.render.RemoveActor(actor)
        self.renWin.Render()
        del self.stl_actors[key]
        
    def add_actor(self, actor):
        self.render.AddActor(actor)
        self.actors.append(actor)
        
        
#    def close_stl(self):
#        if self.stl_actor is not None:
#            self.render.RemoveActor(self.stl_actor)
#        self.stl_actor = None



            


class RendererQtWidget(QWidget):
    # This is actually a vtkwidget within a qt widget
    # This can be embedded into a Qt window
    # Had to fiddle randomly a bit to get it working
    # VTK is designed to work with PyQt4 not 5 (which is not backwards 
    # compatible) so quite surprising any of this actually works

    def __init__(self, app, parent=None):
        self.app = app
        QWidget.__init__(self, parent)

        self.frame = self#QFrame()

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        self.vtk_renderer = VTKRenderer(window=self.vtkWidget.GetRenderWindow(),
                                        window_interactor=self.vtkWidget.GetRenderWindow().GetInteractor())

        self.frame.setLayout(self.vl)
        
        self.open_stl = self.vtk_renderer.open_stl
        self.set_color = self.vtk_renderer.set_color
        
        self.add_actor = self.vtk_renderer.add_actor
        
        self.data_holder = self.vtk_renderer.data_holder
        self.render = self.vtk_renderer.render
        
    def show(self, app=None):
        QWidget.show(self)
        self.vtk_renderer.start()
        self.app.exec_()
        
    @property
    def window_name(self):
        return self.GetWindowTitle()
    
    @window_name.setter
    def window_name(self, name):
        self.setWindowTitle(name)
        
        
        
    start = show



_figure = None

def figure(qt=False, app=None, name="3d_plot"):
    global _figure
    if qt:
        if app is None:
            app = QApplication(sys.argv)
        _figure = RendererQtWidget(app)
    else:
        _figure = VTKRenderer()
    _figure.window_name = name
    return _figure

def gcf():
    global _figure
    if _figure is None:
        _figure = VTKRenderer()
    return _figure
        
def show(clear_fig=True):
    global _figure
    current_fig = gcf()
    if clear_fig:
        _figure = None
    else:
        if isinstance(current_fig, RendererQtWidget):
            _figure = RendererQtWidget(current_fig.app)
        else:
            _figure = VTKRenderer()
        [_figure.add_actor(i) for i in current_fig.render.GetActors()]
    current_fig.start()


def mesh_plot(mesh, tri_scalars=None, scalars=None, color=None, opacity=None):
    fig = gcf()

    vertices = mesh.vectors.reshape((len(mesh) * 3, 3))
    triangles = np.empty((len(mesh), 4), np.int64)
    triangles[:, 0] = 3
    for i in range(3):
        triangles[:, i+1] = np.arange(i, len(mesh) * 3, 3)
        
    triangles = triangles.ravel()
    fig.data_holder.append(triangles)
    fig.data_holder.append(vertices)

    poly_data = vtk.vtkPolyData()
        
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(vertices))        
    poly_data.SetPoints(points)
    
    cells = vtk.vtkCellArray()
    cells.SetCells(len(triangles), numpy_to_vtkIdTypeArray(triangles))
    poly_data.SetPolys(cells)
    
    if tri_scalars is not None:
#        scalars = np.array([tri_scalars, tri_scalars, tri_scalars]).T
        assert tri_scalars.shape == (len(mesh), )
        scalars = np.empty((len(tri_scalars), 3))
        for i in range(3):
            scalars[:, i] = tri_scalars
    
    if scalars is not None:
#        scalars[~np.isfinite(scalars)] = np.nanmean(scalars)
        if scalars.shape != (len(mesh), 3):
            raise ValueError("Expected (n, 3) shape array. Got {}".format(scalars.shape))

        poly_data.GetPointData().SetScalars(numpy_to_vtk(scalars.ravel()))
        fig.data_holder.append(scalars)
 
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)
    if scalars is not None:
        mapper.SetScalarRange(np.nanmin(scalars), np.nanmax(scalars))
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    _color_opacity(actor, color, opacity)
        
    fig.add_actor(actor)
#    print(mesh.name)
    fig.window_name += "; " + nuts_and_bolts.as_str(mesh.name)
    
    return actor, mapper

    
def scalar_bar(plot_output):
    actor, mapper = plot_output
    
    scalar_bar = vtk.vtkScalarBarActor()
#    scalar_bar.SetTitle("ugg")
    
    scalar_bar.SetNumberOfLabels(6)
#    scalar_bar.GetLabelTextProperty().SetFontSize(200)
#    scalar_bar.GetLabelTextProperty().SetColor(.5, .5 ,.5)
#    scalar_bar.GetAnnotationTextProperty().SetFontSize(50)

    scalar_bar.SetLookupTable(mapper.GetLookupTable())
    
    
    gcf().add_actor(scalar_bar)
    


def text(text_str, position=(0, 0), fontsize=18, color=(1, 1, 1)):
#    global txt
    # create a text actor
    txt = vtk.vtkTextActor()
    txt.SetInput(text_str)
    txtprop=txt.GetTextProperty()
    txtprop.SetFontFamilyToArial()
    txtprop.SetFontSize(fontsize)
    txtprop.SetColor(*color)
    txt.SetPosition(*position)
    
    # assign actor to the renderer
    gcf().add_actor(txt)


def _color_opacity(actor, color=None, opacity=None):
    prop = actor.GetProperty()

    if opacity is not None:
        prop.SetOpacity(opacity)
    
    if color is not None:
        if isinstance(color, str):
            color = mpl_colors[color]
        
        prop.SetColor(*color[:3])
        
        if len(color) == 4:
            prop.SetOpacity(color[3])
            
    
    
def _iter_points(points):
    return nuts_and_bolts.flatten_all_but_last(points)


def _iter_colors(colors, shape):
    size = int(np.prod(shape))
    
    if colors is None:
        return (None for i in range(size))
    
    elif isinstance(colors, (tuple, list, str)):
        return (colors for i in range(size))
    
    elif isinstance(colors, np.ndarray) and colors.shape[:-1] == shape:
        return nuts_and_bolts.flatten_all_but_last(colors)
        
    else:
        raise ValueError("colors type not understood")
        
def _iter_scalar(s, shape):
    size = int(np.prod(shape))
    
    s = np.asarray(s)
    if s.shape == ():
        return (s for i in range(size))
    else:
        return s.flat
        
    

def scatter(points, colors=None, opacity=None, radius=1.):
    points = np.asarray(points)
    for (xyz, color) in zip(_iter_points(points), _iter_colors(colors, points.shape[:-1])):
        source = vtk.vtkSphereSource()
        source.SetCenter(*xyz)
        source.SetRadius(radius)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
    
        _color_opacity(actor, color, opacity)
                
        gcf().add_actor(actor)
                
    
def arrow(starts, ends, lengths=None, colors=None, opacity=None):
    
    diffs = ends - starts
    if lengths is None:
        lengths = geom.distance(diffs)
    bases = geom.orthogonal_bases(diffs)
    
    for (start, end, length, base, color) in zip(_iter_points(starts),
                                               _iter_points(ends),
                                               _iter_scalar(lengths, starts.shape[:-1]),
                                               zip(*(_iter_points(eAx) for eAx in bases)),
                                               _iter_colors(colors, starts.shape[:-1])):
        eX, eY, eZ = base
        arrowSource = vtk.vtkArrowSource()
        
        matrix = vtk.vtkMatrix4x4()

        # Create the direction cosine matrix
        matrix.Identity()
        for i in range(3):
          matrix.SetElement(i, 0, eX[i])
          matrix.SetElement(i, 1, eY[i])
          matrix.SetElement(i, 2, eZ[i])
        
        # Apply the transforms
        transform = vtk.vtkTransform()
        transform.Translate(start)
        transform.Concatenate(matrix)
        transform.Scale(length, length, length)
        
        
        #Create a mapper and actor for the arrow
        mapper = vtk.vtkPolyDataMapper()
        actor = vtk.vtkActor()
        
        mapper.SetInputConnection(arrowSource.GetOutputPort())
        actor.SetUserMatrix(transform.GetMatrix())
        
        actor.SetMapper(mapper)

        _color_opacity(actor, color, opacity)
                
        
        
        gcf().add_actor(actor)
        
#        print("adding", actor)

        
def quiver(points, gradients, lengths=None, length_scale=1, colors=None, opacity=None):
    if lengths is None:
        lengths = geom.distance(gradients)
    if length_scale != 1:
        lengths *= length_scale
        
    arrow(points, points + gradients, lengths, colors, opacity)
        


def plot(vertices, color=None, opacity=None, line_width=1.0, join_ends=False):
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(vertices))
    
    
    # vtkCellArray is a supporting object that explicitly represents cell connectivity.
    # The cell array structure is a raw integer list of the form:
    # (n,id1,id2,...,idn, n,id1,id2,...,idn, ...) where n is the number of points in
    # the cell, and id is a zero-offset index into an associated point list.
    
    point_args = np.empty(1 + len(vertices) + join_ends, np.int64)
    point_args[0] = len(vertices) + join_ends
    point_args[1: 1+len(vertices)] = np.arange(len(vertices))
    if join_ends:
        point_args[-1] = 0
    lines = vtk.vtkCellArray()
    lines.SetCells(len(point_args), numpy_to_vtkIdTypeArray(point_args.ravel()))
    
    
    # vtkPolyData is a data object that is a concrete implementation of vtkDataSet.
    # vtkPolyData represents a geometric structure consisting of vertices, lines,
    # polygons, and/or triangle strips
    polygon = vtk.vtkPolyData()
    polygon.SetPoints(points)
    polygon.SetLines(lines)
    
    
    # Create an actor to represent the polygon. The actor orchestrates rendering of
    # the mapper's graphics primitives. An actor also refers to properties via a
    # vtkProperty instance, and includes an internal transformation matrix. We
    # set this actor's mapper to be polygonMapper which we created above.
    polygonActor = vtk.vtkActor()
    
    fig = gcf()
    
#    if scalars is not None:
#        polygon.GetCellData().SetScalars(numpy_to_vtk(scalars))
#        fig.data_holder.append(scalars)
        
#    elif colors is not None:
#        print(colors.shape)
#        colors = np.asarray(colors)
#        if len(colors.shape) == 1:
#            _color_opacity(polygonActor, colors, opacity)
            
#        elif len(colors.shape) == 2:
#            print("ugg")
#            if colors.max() <= 1 and colors.dtype.kind not in "ui":
#                colors = colors * 255
#            colors = colors.astype(np.uint8)
#            if colors.shape[-1] == 4:
#                print("Per line opacity is not supported")
#                colors = colors[..., :3]
#            print(colors)
#    fig.data_holder.append(colors)
#    colors_ = numpy_to_vtk(colors)
#    polygon.GetCellData().SetScalars(colors_)
            
#        else:
#            assert 0
            
    _color_opacity(polygonActor, color, opacity)
    polygonActor.GetProperty().SetLineWidth(line_width)
#    polygonActor.GetProperty().SetRenderLinesAsTubes(1)


    # vtkPolyDataMapper is a class that maps polygonal data (i.e., vtkPolyData)
    # to graphics primitives
    polygonMapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        polygonMapper.SetInputConnection(polygon.GetProducerPort())
    else:
        polygonMapper.SetInputData(polygon)
        polygonMapper.Update()

    polygonActor.SetMapper(polygonMapper)
    
    
    fig.add_actor(polygonActor)
    

def view(focal_point=None, camera_position=None, up_view=None):
    fig = gcf()
    camera = fig.render.GetActiveCamera()
    if focal_point is not None:
        camera.SetFocalPoint(*focal_point)
    if camera_position is not None:
        camera.SetPosition(*camera_position)
    if up_view is not None:
        camera.SetViewUp(*up_view)
    return camera.GetFocalPoint(), camera.GetPosition(), camera.GetViewUp()

#def view_relative(focal_point, camera_distance, camera_direction)

def reset_camera():
    gcf().render.ResetCamera()


def save_fig(path, scale=1):
    if not isinstance(path, Path):
        path = Path(path)
        
    fig = gcf()
    renWin = fig.renWin
    renWin.Render()
    
    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.SetScale((scale, scale))
    w2if.Update()

    old_path = Path.cwd()
    os.chdir(path.parent)
    if path.suffix.lower() in (".jpg", ".jpeg"):
        writer = vtk.vtkJPEGWriter()
    elif path.suffix.lower() == ".png":
        writer = vtk.vtkPNGWriter()
    else:
        raise NotImplementedError(path.suffix + " is not supported")
    writer.SetFileName(path.name)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()
    os.chdir(old_path)

def close():
    global _figure
    fig = gcf()
    fig.iren.GetRenderWindow().Finalize()
    fig.iren.TerminateApp()
    _figure = None


def text3d(string, position=(0, 0, 0), follow_cam=True, scale=1, color=None, opacity=None):
    # Create the 3D text and the associated mapper and follower (a type of
    # actor). Position the text so it is displayed over the origin of the
    # axes.
    if np.isscalar(scale):
        scale = (scale, ) * 3
        
    if not isinstance(string, str):
        string = str(string)
    
    source = vtk.vtkVectorText()
    source.SetText(string)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    
    actor = vtk.vtkFollower()
    actor.SetMapper(mapper)
    actor.SetScale(*scale)
    actor.SetPosition(*position)
    _color_opacity(actor, color, opacity)
    
    if follow_cam:
        actor.SetCamera(gcf().render.GetActiveCamera())

    
    gcf().add_actor(actor)



def polygon(vertices, color=None, opacity=None):
    # vtkPolyData is a data object that is a concrete implementation of vtkDataSet.
    # vtkPolyData represents a geometric structure consisting of vertices, lines,
    # polygons, and/or triangle strips
    polygon = vtk.vtkPolyData()
    
    
    
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(vertices))        
    polygon.SetPoints(points)
    
    
    # vtkCellArray is a supporting object that explicitly represents cell connectivity.
    # The cell array structure is a raw integer list of the form:
    # (n,id1,id2,...,idn, n,id1,id2,...,idn, ...) where n is the number of points in
    # the cell, and id is a zero-offset index into an associated point list.
    
    point_args = np.empty(1 + len(vertices), np.int64)
    point_args[0] = len(vertices)
    point_args[1: 1+len(vertices)] = np.arange(len(vertices))
    polys = vtk.vtkCellArray()
    polys.SetCells(1, numpy_to_vtkIdTypeArray(point_args.ravel()))
    
    lines = vtk.vtkCellArray()
    lines.SetCells(len(point_args), numpy_to_vtkIdTypeArray(point_args.ravel()))
    
    
    polygon.SetPolys(polys)
    polygon.SetLines(lines)
    
    # vtkPolyDataMapper is a class that maps polygonal data (i.e., vtkPolyData)
    # to graphics primitives
    polygonMapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        polygonMapper.SetInputConnection(polygon.GetProducerPort())
    else:
        polygonMapper.SetInputData(polygon)
        polygonMapper.Update()
    
    # Create an actor to represent the polygon. The actor orchestrates rendering of
    # the mapper's graphics primitives. An actor also refers to properties via a
    # vtkProperty instance, and includes an internal transformation matrix. We
    # set this actor's mapper to be polygonMapper which we created above.
    polygonActor = vtk.vtkActor()
    polygonActor.SetMapper(polygonMapper)
    
    polygonActor
    _color_opacity(polygonActor, color, opacity)
    
    gcf().add_actor(polygonActor)
    

def annotate(points, text, direction, text_color="w", arrow_color="k", distance=3, text_size=1):
    point = geom.highest(points, direction)
    text_point = point + distance * direction
    arrow(text_point, point, colors=arrow_color)
    text3d(text, text_point, color=text_color, scale=text_size)


if __name__ == '__main__':

    from stl.mesh import Mesh
    #from Mesh_class import Mesh
    

    QT = False
    
    fig = figure(QT, name="socks")

#    window = gcf()
    path = next(Path('C:/Users/Brénainn/Documents/uni/project/stl').glob("*.stl"))
#    path = QFileDialog.getOpenFileName()[0]
    
##    window.open_stl((path, ""))
    mesh = Mesh.from_file(path)
    mesh.name = path.name
##    pd = reader.GetOutput()
#    
#    
#
    scalars = mesh.vectors[:, :, 2].copy()#.ravel() 
    scalars[:100] = np.nan
#    tri_scalars = mesh.areas.ravel()
##    scalars -= scalars.min()
##    scalars /= scalars.max()
#
    scalar_bar(mesh_plot(mesh, 
#              color=(.8, .3, .4),
              scalars=scalars,
#              tri_scalars=tri_scalars,
#              opacity=.6,
              )
    )
#    
#    text("Hello World")
#    text("Hello World\nbacon", (0, 18), 20, (1, 0, 0))
    text3d("text", (0, 0, 5), color="g")
#    
#    show()
#    import copy
#    mesh2 = copy.deepcopy(mesh)
#    mesh2.translate(np.array([3, 3, 50]))
#    mesh_plot(mesh2, 
#              color=(.8, .3, .4),
##              scalars=scalars,
#              opacity=.6,
#              )
    
    vertices = np.random.uniform(-30, 30, (3, 3))
    ends = np.random.uniform(-10, 10, (20, 3, 3))
    quiver(vertices, ends, colors=vertices)
    
#    colors = np.random.randint(0, 256, size=vertices.shape, dtype=np.uint8)
    plot(vertices, color=(.6, .4, .2), line_width=5, join_ends=True)
#    
#        
#    save_fig(path.with_suffix(".png"), 10)
#    close()
    reset_camera()
    show()
#        
#    
#        
#    
#    
#

