# Building the docs

The documentation can either be built statically using the conventional:

```shell script
make html
```
Or if you `pip install sphinx-autobuild` you can build dynamically (all changes
updated automatically and your browser refreshed) using on Unix:

```shell script
source autobuild
```

Or on Windows:

```shell script
type autobuild | cmd
```

In both cases your working directory must be this `docs` folder rather than the
repo's root.
