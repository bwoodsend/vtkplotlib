# Welcome to the vtkplotlib test suite!

This guide explains how to run the test suite.

## Test requirements

Some tests for features requiring extra optional dependencies are conditionally skipped if that library isn't installed. To install only the basics use (in the root of this repository):

```shell
pip install .[test_minimal]
```

Or to get everything:

```shell
pip install .[test_full]
```

In either case you may use the `-e` parameter.

## Run the tests

The test-suite is a `pytest` one. Use (in the root of this repository):

```shell
pytest tests
```

Or, if your working directory is not the root of this repo:

```shell
pytest /full/or/relative/path/to/tests
```

It's not particularly well automated. You still have to click and close through each window. I have made a few attempts to improve this but not with much success.

Be sure to test on Python 2.7 and 3.5 as well as your go-to version.

## Testing with PyInstaller

### Setup

To do this requires a PyInstaller that is recent enough to allow libraries to provide their own hooks:

``` shell
pip install "PyInstaller>=4.0"
```

And make sure your `matplotlib` is older than `3.3.0`.

```shell
pip install "matplotlib<3.3"
```

### Build

Next `cd` into the `./tests/PyInstaller/` directory and run:

```shell
PyInstaller --clean --noconfirm test.spec
```

The `--noconfirm` is optional. And `--clean` is only necessary if you have changed the *vtkplotlib* source code.

This creates an executable at `./dist/test/test` (or `dist\test\test.exe` on Windows). 

### Test

This executable is just `pytest.main()` with *vtkplotlib* installed in it. The tests themselves are excluded. Run it as you would run `pytest`. Assuming the working directory is still `./tests/PyInstaller/` use:

```shell
dist/test/test ../
```

Avoid running it with the root of this repo as the current working directory. Otherwise you may unintentionally use the original source *vtkplotlib* rather than the bundled one.

