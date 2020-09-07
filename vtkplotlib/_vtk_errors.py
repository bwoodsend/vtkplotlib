# -*- coding: utf-8 -*-
# =============================================================================
# Created on Wed Aug 14 21:23:22 2019
#
# @author: Brénainn Woodsend
#
#
# _vtk_errors.py listens to VTK errors and prints them to stdout.
# Copyright (C) 2019-2020  Brénainn Woodsend
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

import traceback
from builtins import super


class ErrorObserver(object):

    def __init__(self):
        self.CallDataType = 'string0'
        self.messages = set()

    def __call__(self, obj, event, message):
        if message not in self.messages:
            print(message)
            self.messages.add(message)

    def attach(self, vtk_obj):
        vtk_obj.AddObserver("ErrorEvent", self)


class ErrorSilencer(ErrorObserver):

    def __call__(self, obj, event, message):
        pass


class VTKException(Exception):
    pass


class VTKErrorRaiser(ErrorObserver):
    error_message = None

    def __init__(self, vtk_obj):
        super().__init__()
        self.attach(vtk_obj)

    def __call__(self, obj, event, message):
        self.error_message = message
        self.stack = traceback.extract_stack()

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        if self.error_message is not None:
            raise VTKException(self.error_message)


handler = ErrorObserver()
silencer = ErrorSilencer()

if __name__ == "__main__":
    pass
