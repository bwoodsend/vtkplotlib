========================
Looking up original data
========================

The coordinates given by :attr:`pick.point` interpolate between vertices you
have provided. If you require the nearest user-provided coordinate then you must
implement this yourself.

You can do this either using brute-force:

.. code-block:: python

    closest_arg = vpl.geometry.distance(vertices - pick.point).argmin()
    closest_point = vertices[closest_arg]

Or, for time-critical applications, using a KDTree from either
`scipy's cKDTree`_ or `pykdtree`_ (demonstrated below).

.. _`scipy's cKDTree`: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.html
.. _pykdtree: https://github.com/storpipfugl/pykdtree

.. code-block:: python

    import vtkplotlib as vpl
    import numpy as np
    from pykdtree.kdtree import KDTree

    # Create a figure.
    fig = vpl.figure()

    # Add something to write into.
    output = vpl.text("", color="k")

    # Add something with some made-up per-vertex scalars.
    mesh = vpl.mesh_plot(vpl.data.get_rabbit_stl())
    mesh.scalars = scalars = mesh.vertices[..., 0] * mesh.vertices[..., 2] / 1000
    vpl.scalar_bar(mesh)

    # Finally - the interesting bits...

    # Create a tree to facilitate fast lookup. Be careful of float types.
    tree = KDTree(mesh.vertices.astype(float))

    def callback(invoker, event_name):
        pick = vpl.i.pick(fig)

        # If mouse if over the rabbit.
        if pick.actor_3D is not None:
            # pykdtree is fussy in that you must use a 2D array - even if you're
            # only querying one point.
            distance, arg = tree.query(np.atleast_2d(pick.point))
            output.text = "The scalar value at {} is {}".format(
                np.round(pick.point, 3), np.round(scalars[arg], 3)
            )
        else:
            output.text = "Hover the mouse over the rabbit"

        vpl.i.call_super_callback()
        fig.update()

    fig.style.AddObserver("MouseMoveEvent", callback)

    fig.show()

Note that having a `MouseMoveEvent` which modifies the contents of a figure and
therefore requires ``fig.update()`` to be called for every such event requires a
lot of processing power. A better option is to use an output outside of the
renderer such as a :meth:`QtWidgets.QLabel`.
