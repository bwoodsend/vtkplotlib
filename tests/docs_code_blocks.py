# -*- coding: utf-8 -*-
"""
Pull and test code-blocks from docstrings. I'm 100% certain this must be a
reinvention of the wheel but I can only find doc-testing for interactive console
style code examples.
"""

from __future__ import print_function, with_statement
from builtins import super

import re
import types
import itertools

_code_blocks_re = re.compile(
    r"(?:^|\n)( *)\.\. code-block:: python\n((?:(?:\1 .*)| *\n)*)")


def code_blocks_from_str(doc):
    """
    Find all code-blocks in a string.

    :param doc: A docstring.
    :return: list of (line_number: int, block: str).

    Blocks that don't contain `import vtkplotlib as vpl` are skipped as these
    are just fragments rather than self-contained examples. The original
    indentation is not removed.
    """
    out = []
    for i in _code_blocks_re.finditer(doc):
        block = i.group(2)
        if "import vtkplotlib as vpl" in block:
            first_line_no = doc[:i.start(1)].count("\n")
            out.append((first_line_no, block))
    return out


def code_block_to_test(first_line_no, block, name, filename):
    """
    """
    body = first_line_no * "\n" + "def {}():\n".format(name) + block
    dic = {}
    exec(compile(body, filename, "exec"), dic, dic)
    return dic[name]


def _get_doc(obj):
    doc = getattr(obj, "__doc__", "") or ""
    return doc if isinstance(doc, str) else ""


def doc_able(obj):
    types_ = (type, types.MethodType, types.FunctionType, types.ModuleType,
              property)
    return isinstance(obj, types_)


def docs_from_objects(obj):
    to_do = {obj}
    done = {}
    while to_do:
        obj = to_do.pop()
        done[obj] = _get_doc(obj)
        try:
            vars(obj)
        except TypeError:
            continue
        for (name, attr) in vars(obj).items():
            if not doc_able(attr):
                continue
            try:
                if attr not in done:
                    to_do.add(attr)
            except TypeError:
                # Skip un-hashable.
                continue

    return done


def code_blocks_from_objects(obj):
    out = {}
    for (obj, doc) in docs_from_objects(obj).items():
        blocks = code_blocks_from_str(doc)
        if blocks:
            out[obj] = blocks
    return out


def _name_object(obj):
    _repr = repr(getattr(obj, "fget", obj))
    return re.sub(r"\W+", "_", _repr.replace(".", "_"))


counter = itertools.count()


def tests_from_doc(doc, file="<string>"):
    out = {}
    for (i, block) in zip(counter, code_blocks_from_str(doc)):
        name = "test_%i" % i
        out[name] = code_block_to_test(block[0], block[1], name, file)
    return out


if __name__ == "__main__":
    import vtkplotlib as vpl

    tests_from_doc(vpl.i.__doc__, vpl.i.__file__)
