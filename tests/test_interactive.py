# -*- coding: utf-8 -*-
"""Test the contents of the vtkplotlib.interactive module."""

import pytest
import vtkplotlib as vpl

pytestmark = pytest.mark.order(10)


@pytest.mark.parametrize("invoker", [vpl.gcf().style, vpl.gcf().iren])
@pytest.mark.parametrize("command", vpl.i.vtkCommands)
def test_super_command(invoker, command):
    cb = vpl.i.get_super_callback(invoker, command)
    assert cb is vpl.i.null_super_callback or cb.__self__ is invoker


def test_raise():
    with pytest.raises(RuntimeError):
        vpl.i.get_super_callback()

    def _test(x, y, z):
        vpl.i.get_super_callback()

    with pytest.raises(RuntimeError):
        _test(1, 2, 3)


from tests import docs_code_blocks
for (obj, doc) in docs_code_blocks.docs_from_objects(vpl.i).items():
    globals().update(docs_code_blocks.tests_from_doc(doc, repr(obj)))

if __name__ == "__main__":
    pytest.main([__file__])
