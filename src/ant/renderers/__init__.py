"""Rendering utilities for Langton ant simulations."""
from ant.renderers.ascii import AsciiRenderer
from ant.renderers.live import LiveAsciiRunner

try:  # pragma: no cover - optional dependency import
    from ant.renderers.mpl import MatplotlibAnimator, run_matplotlib
except ImportError:  # pragma: no cover - matplotlib not installed
    MatplotlibAnimator = None  # type: ignore[assignment]
    run_matplotlib = None  # type: ignore[assignment]

__all__ = ["AsciiRenderer", "LiveAsciiRunner"]
if MatplotlibAnimator is not None:  # pragma: no cover - conditional export
    __all__.extend(["MatplotlibAnimator", "run_matplotlib"])
