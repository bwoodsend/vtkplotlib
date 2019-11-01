# -*- coding: utf-8 -*-
# =============================================================================
# Created on Wed Aug 14 21:23:22 2019
#
# @author: Brénainn Woodsend
#
#
# _vtk_errors.py listens to VTK errors and prints them to stdout.
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



class ErrorObserver:

    def __init__(self):
        self.CallDataType = 'string0'
        self.messages = set()

    def __call__(self, obj, event, message):
        if message not in self.messages:
            print(message)
            self.messages.add(message)

    def attach(self, vtk_obj):
        vtk_obj.AddObserver("ErrorEvent", self)



handler = ErrorObserver()


if __name__ == "__main__":
    pass
