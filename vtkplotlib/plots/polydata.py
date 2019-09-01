# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 17:44:33 2019

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
from pathlib2 import Path
import vtk
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    get_vtk_to_numpy_typemap
                                    )
import itertools

ID_ARRAY_NUMPY_DTYPE = get_vtk_to_numpy_typemap()[vtk.VTK_ID_TYPE]

#def unpack_id_array(arr, max_size):
#    
    

_numpy_to_vtk = numpy_to_vtk
def numpy_to_vtk(num_array, deep=0, array_type=None):
    assert deep or num_array.flags.contiguous
    return _numpy_to_vtk(np.ascontiguousarray(num_array), deep, array_type)


def cell_array_handler_property(name, doc=""):
    def getter(self):
        lines = getattr(self.vtk_polydata, "Get{}".format(name))()
        length = lines.GetNumberOfCells()
        if length:
            arr = vtk_to_numpy(lines.GetData())
            return unpack_lengths(arr)
        else:
            return []
   
    def setter(self, ids):
        if len(ids):
            ids = pack_lengths(ids)
            lines = vtk.vtkCellArray()
            lines.SetCells(len(ids), numpy_to_vtkIdTypeArray(ids.astype(ID_ARRAY_NUMPY_DTYPE).ravel(), deep=True))
            getattr(self.vtk_polydata, "Set{}".format(name))(lines)
        else:
            getattr(self.vtk_polydata, "Set{}".format(name))(None)
        
    
    def deleter(self):
        setter(self, [])
        
    
    return property(getter, setter, deleter, doc)
        
        


def join_line_ends(lines):
    lines = np.asarray(lines)
    
    if lines.dtype == object:
        out = np.empty(lines.size, object)
        for (i, line) in enumerate(lines.flat):
            out[i] = line[np.arange(max(-1, -len(line)), len(line))]
        return out

    else:
        n, m = lines.shape
        return lines[:, np.arange(max(-1, -m), m)]
        
    

def pack_lengths(itr_of_arrays):
    if not isinstance(itr_of_arrays, (list, np.ndarray)):
        itr_of_arrays = list(itr_of_arrays)
    itr_of_arrays = np.asarray(itr_of_arrays)
    
    if itr_of_arrays.dtype == object:
        parts = itertools.chain(*[([len(i)], i) for i in itr_of_arrays.flat])
        return np.concatenate(list(parts))
    
    else:
        from vtkplotlib.nuts_and_bolts import flatten_all_but_last
        
        itr_of_arrays = flatten_all_but_last(itr_of_arrays)
        n, m = itr_of_arrays.shape
        lengths = np.ones((n, 1), int) * m
        return np.concatenate([lengths, itr_of_arrays], axis=1)
    
    
    
def unpack_lengths(arr):
    assert len(arr.shape) == 1
    
    def error_msg():
        print("Warning - checksum failed. This input array will cause VTK to crash if plotted.")
    
    if len(arr) == 0:
        return []
    
    m = arr[0]
    if (m == arr[::m+1]).all():
        if len(arr) % (m+1):
            error_msg()
        return arr.reshape((len(arr) // (m+1), m+1))[:, 1:]
    
    else:
        i = 1
        out = []
        while True:
            j = i + m
            if j > len(arr):
                error_msg()
                break
            else:
                out.append(arr[i: j])
                if j == len(arr):
                    break
                else:
                    m = arr[j]
                    i = j + 1
        
        return out
    
    
    
############################################################################
    


class PolyData(object):
    def __init__(self, vtk_polydata = None):
        self.vtk_polydata = vtk_polydata or vtk.vtkPolyData()
        
#        self.points = []
#        self.lines = []
        
    @property
    def points(self):
        points = self.vtk_polydata.GetPoints()
        if points is None:
            return None
        else:
            return vtk_to_numpy(points.GetData())
        
    @points.setter
    def points(self, vertices):
        vertices = np.ascontiguousarray(vertices)
        
        if vertices is None:
            self.vtk_polydata.SetPoints(None)
        else:
            points = vtk.vtkPoints()
            points.SetData(numpy_to_vtk(vertices, deep=True))
            self.vtk_polydata.SetPoints(points)

        
    lines = cell_array_handler_property("Lines")

    polygons = cell_array_handler_property("Polys")
        
    
    def __repr__(self):
        out = ["%s {\n" % self.__class__.__name__]
        for i in "points lines polygons".split():
            x = getattr(self, i)
            if x is not None:
                x = len(x)
            out.append("    {} {}{}\n".format(x, i[:-1], ("", "s")[x != 1]))
        out.append("}\n")
            
        return "".join(out)
    
    
    def to_plot(self, fig="gcf"):
        from vtkplotlib.plots.BasePlot import ConstructedPlot
        plot = ConstructedPlot(fig)
        plot.polydata = self
        plot.add_to_plot()
        return plot
    
    
    @property
    def point_scalars(self):
        scalars = self.vtk_polydata.GetPointData().GetScalars()
        if scalars is None:
            return
        return vtk_to_numpy(scalars)
    
    @point_scalars.setter
    def point_scalars(self, scalars):
        
        if scalars is not None:
            scalars = numpy_to_vtk(np.ascontiguousarray(scalars).reshape((scalars.size, 1)), deep=True)
        scalars = self.vtk_polydata.GetPointData().SetScalars(scalars)
        
    @point_scalars.deleter
    def point_scalars(self):
        self.point_scalars = None
        
        
    

#    _keys = {key for (key, val) in vars().items() if isinstance(val, property)}
#        
#    def __getstate__(self):
#        state = {key: getattr(self, key) for key in self._keys}
#        state["vtk_polydata"] = None
#        return state
#    
#    @classmethod
#    def __setstate__(cls, state):
#        newone = cls()
#        newone.vtk_polydata
##        print(state)
#        for i in state.items():
#            if i[0] == "vtk_polydata":
#                i = "vtk_polydata", vtk.vtkPolyData()
#            setattr(newone, *i)
#        print(newone.vtk_polydata)
#        print(id(newone))
#        return newone
#
#    def __deepcopy__(self, memo):
#        import pickle
#        return pickle.loads(pickle.dumps(self))

    
    
    def quick_show(self):
        import vtkplotlib as vpl
        old_fig = vpl.gcf(create_new=False)
        
        fig = vpl.figure(repr(self))
        self.to_plot(fig)
        vpl.show(fig)
        
        vpl.scf(old_fig)
        
        
    def __add__(self, other):
        assert isinstance(other, self.__class__)
        new = self.__class__()
        points = [self.points, other.points]
        points[1] = points[1].astype(points[0].dtype)
        new.points = np.concatenate(points)
        
        for attr in ("polygons", "lines"):
            lines = [getattr(self, attr), getattr(other, attr)]
            try:
                lines[1] = lines[1] + len(points[0])
            except:
                for i in lines[1]:
                    i += len(points[0])
                    
            try:
                lines = np.concatenate(lines)
            except ValueError:
                lines = list(lines[0]) + list(lines[1])
                
            setattr(new, attr, lines)
        
        scalars = [self.point_scalars, other.point_scalars]
        for i in range(2):
            if scalars[i] is None:
                scalars[i] = np.zeros(len(points[i]))
        new.point_scalars = np.concatenate(scalars)
        
        return new
        

    
        

if __name__ == "__main__":
    import vtkplotlib as vpl
    
    t = np.arange(0, 1, .01) * 2 * np.pi
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)], dtype=np.float32).T
    
    path = Path(vpl.data.get_rabbit_stl())
    
    
    other = vpl.plot(points, color="r").polydata
#    self = PolyData()
#    self.points = points
##    
##    n, m = 10, 50
##    itr_of_arrays = np.random.randint(0, len(points), (n, m))
###    lines = np.concatenate((np.ones((n, 1), int) * m, lines), axis=1)
##    
    lines = [np.random.randint(0, len(t), np.random.randint(3, 5)) for i in range(10)]
    self = vpl.plots.polydata.PolyData()
    self.points = points
    self.lines = join_line_ends(lines)
    self.to_plot()
    
    
#    
#    from stl.mesh import Mesh
#    vectors = Mesh.from_file(vpl.data.get_rabbit_stl()).vectors
    
#    points = vpl.nuts_and_bolts.flatten_all_but_last(vectors)
#    self.points = points
#    polygons = np.arange(len(points)).reshape((len(points) // 3, 3))
#    self.polygons = polygons
    
#    point_scalars = points[:, np.newaxis, 0]
##    self.vtk_polydata.GetPointData().SetScalars(numpy_to_vtk(point_scalars.astype(np.float64), deep=True))
#    self.point_scalars = point_scalars
    
#    plot = self.to_plot()
##    plot.mapper.SetScalarRange(np.nanmin(point_scalars), np.nanmax(point_scalars))
##    plot.property.SetLineWidth(4.)
    vpl.show()
