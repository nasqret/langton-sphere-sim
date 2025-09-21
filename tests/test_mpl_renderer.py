from __future__ import annotations

import warnings

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

warnings.filterwarnings(
    "ignore",
    message="Animation was deleted without rendering anything",
    category=UserWarning,
    module="matplotlib.animation",
)

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from ant.core.direction import Heading
from ant.core.simulation import Ant, Simulation
from ant.renderers.mpl import MatplotlibAnimator


@pytest.fixture
def simulation() -> Simulation:
    ants = [
        Ant(ant_id=1, x=0, y=0, heading=Heading.NORTH, trail_color="red"),
        Ant(ant_id=2, x=1, y=0, heading=Heading.EAST, trail_color="blue"),
    ]
    sim = Simulation(width=4, height=3, ants=ants)
    # Seed some trails
    sim.grid.mark_trail(0, 0, 1, lifetime=5)
    sim.grid.mark_trail(1, 0, 2, lifetime=5)
    return sim


def test_matplotlib_animator_builds_frame(simulation: Simulation) -> None:
    animator = MatplotlibAnimator(simulation, frame_interval_ms=10)
    frame = animator._build_frame()
    assert frame.shape == (simulation.grid.height, simulation.grid.width)
    assert isinstance(frame, np.ndarray)
    # Active ants should occupy dedicated bins (> base values)
    assert frame[0, 0] > 1
    assert frame[0, 1] > 1
    assert "steps: 0" in animator._annotation.get_text()
    assert "topology:" in animator._annotation.get_text()


def test_matplotlib_animator_updates_state(simulation: Simulation) -> None:
    animator = MatplotlibAnimator(simulation, frame_interval_ms=10)
    # Trigger an update to ensure simulation advances
    animator._update(0)
    assert simulation.steps_executed == 1
    assert "steps: 1" in animator._annotation.get_text()


@pytest.mark.filterwarnings("ignore:Animation was deleted:UserWarning")
def test_matplotlib_animator_creates_animation(simulation: Simulation) -> None:
    animator = MatplotlibAnimator(simulation, frame_interval_ms=5)
    animation = animator.create_animation(steps=3)
    assert isinstance(animation, FuncAnimation)
    plt.close(animator._figure)


def test_matplotlib_animator_run_can_save(monkeypatch, simulation: Simulation, tmp_path) -> None:
    animator = MatplotlibAnimator(simulation, frame_interval_ms=10)

    class DummyAnimation:
        def __init__(self) -> None:
            self.saved: tuple[str, dict] | None = None

        def save(self, path: str, **kwargs) -> None:
            self.saved = (path, kwargs)

    dummy = DummyAnimation()
    monkeypatch.setattr(animator, "create_animation", lambda steps=None: dummy)

    target = tmp_path / "demo.gif"
    animator.run(steps=2, show=False, save_path=str(target), save_kwargs={"fps": 15})

    assert dummy.saved == (str(target), {"fps": 15})
