# Contributing to vtkplotlib

Contribution and communication guide.

---------------------------------------------------------------------------

## General feedback or suggestions

For either the API or the docs use the [github issues page](https://github.com/bwoodsend/vtkplotlib/issues/) and mark it with an appropriate label.



## Bug report

To report an issue or to point out undesirable behavior, please use the [issues page](https://github.com/bwoodsend/vtkplotlib/issues/). Please include:

*  vtkplotlib version.
* Versions of all libraries listed under [*Requirements for installing*](https://vtkplotlib.readthedocs.io/en/latest/#requirements-for-installing) and [*Optional requirements*](https://vtkplotlib.readthedocs.io/en/latest/#optional-requirements) in our [quickstart](https://vtkplotlib.readthedocs.io/en/latest/) page. (Use `pip show numpy` or `pip freeze -> packages.txt` to find these versions.)
* Python version.
* Whether or not you use Anaconda.
* OS.
* Along with the usual, what did you do? And what did vtkplotlib do wrong?



## Request new features

To request a feature, either create an issue or just ping me at <bwoodsend@gmail.com>. This library has rather grown organically as I need new features for other projects. Other features are generally not included because I haven't needed them yet rather than because they would be too much hassle. There are loads of VTK classes which I haven't ported over but would be easy (couple of hours work max) from me to do so. You can search online for `vtk [feature_name] example` (it'll likely be in C++ which is OK) or rummage around in the VTK namespace to see if one exists. If it doesn't then submit an issue anyway and I'll see what I can do. If you want to be specific or just to help you can sketch out the function. Something like the following would help. It doesn't need to be properly typeset.

```python
def exciting_new_feature(some, key, parameters, or, options, you, think, youll, need):
    # Some vague info about the types, desired effect, defaults of each parameter from
    # above. Doesn't have to be complete.

    # Any handy little (type) abstractions you can would like. Such as:
    if not isinstance(text_parameter, str):
        text_parameter = str(text_parameter)
	# It doesn't have to be proper code.

    # leave the implementation to me...
    # unless you have any suggestions

    return # What, if anything, should come out?
```

Or whatever you feel makes the point...



## Documentation suggestions

To suggest a documentation improvement, or to point out a function or component that is poorly documented or completely undocumented, submit an issue along with the url or function / class name or attribute that needs changing along with any suggested text if you have any.



## Write your own feature

You are welcome to this, but if it's a one off and you're not already familiar with VTK, then you're probably better off just to request it. The learning curve for VTK is steep, and the internals of vtkplotlib are pretty unorganized. But if you're determined then don't let me stop you. One day I'll get round to documenting all the core base classes used to add new features, but until then, feel free to ping me <bwoodsend@gmail.com> first for guidance. I have a few features half-prepped hidden away and unexposed so you may not need to start from scratch.

If you do know VTK, then you may find it easier to write a pure VTK proof of concept script and I'll handle the rest. Please don't waste time trying to re-implement a particular piece of API such as ``color="string"`` arguments - there are base classes and internal methods for doing these which I can link up in seconds.

You can either create a fork, and then a pull request, or you can just write a separate script that runs, using VTK and/or vtkplotlib (or anything else) and I'll turn it into a vtkplotlib feature.



## Become a collaborator

If you want to join the team then cool - you're hired! Again, email me. You will need a fairly good understanding of VTK or be willing to learn it. I'll eventually write a proper description of the library's internals to guide you.


