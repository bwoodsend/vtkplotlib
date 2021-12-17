# -*- coding: utf-8 -*-

import traceback


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
