import pytest


@pytest.fixture(autouse=True)
def close_all_windows():
    """Close all open Qt Windows before and after each test."""
    import vtkplotlib as vpl

    def _close_all_figures():
        for figure in vpl.figure_history:
            try:
                figure.close()
            except RuntimeError:
                pass

    _close_all_figures()
    yield
    _close_all_figures()
