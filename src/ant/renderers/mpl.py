"""Matplotlib-based animation utilities for Langton ant simulations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence
import warnings

warnings.filterwarnings(
    "ignore",
    message="Animation was deleted without rendering anything",
    category=UserWarning,
    module="matplotlib.animation",
)

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap

from ant.core.simulation import Simulation


@dataclass
class MatplotlibAnimator:
    """Render a simulation using Matplotlib's animation tools."""

    simulation: Simulation
    frame_interval_ms: int = 100
    figure_size: tuple[int, int] | None = (6, 6)
    steps_per_frame: int = 1

    def __post_init__(self) -> None:
        if self.frame_interval_ms < 0:
            msg = "frame_interval_ms must be non-negative"
            raise ValueError(msg)
        if self.figure_size is not None and (
            self.figure_size[0] <= 0 or self.figure_size[1] <= 0
        ):
            msg = "figure_size values must be positive"
            raise ValueError(msg)
        if self.steps_per_frame <= 0:
            msg = "steps_per_frame must be positive"
            raise ValueError(msg)

        self._figure, self._axis = plt.subplots(figsize=self.figure_size)
        self._axis.set_title("Langton Ant Simulator")
        self._axis.set_xticks([])
        self._axis.set_yticks([])
        self._axis.set_aspect("equal")
        self._axis.invert_yaxis()

        self._trail_indices = {
            ant.ant_id: index for index, ant in enumerate(self.simulation.ants, start=2)
        }
        self._active_indices = {
            ant.ant_id: index
            for index, ant in enumerate(
                self.simulation.ants, start=2 + len(self.simulation.ants)
            )
        }
        cmap_colors = ["white", "black"] + [
            ant.trail_color for ant in self.simulation.ants
        ]
        cmap_colors.extend(ant.trail_color for ant in self.simulation.ants)
        self._colormap = ListedColormap(cmap_colors)
        self._max_index = 2 + 2 * len(self.simulation.ants)

        initial_frame = self._build_frame()
        self._image = self._axis.imshow(
            initial_frame,
            cmap=self._colormap,
            vmin=0,
            vmax=max(1, self._max_index),
            interpolation="nearest",
        )
        self._steps_remaining: Optional[int] = None
        self._annotation = self._axis.text(
            0.02,
            0.95,
            "",
            transform=self._axis.transAxes,
            ha="left",
            va="top",
            color="white",
            bbox={"facecolor": "black", "alpha": 0.5, "pad": 4, "edgecolor": "none"},
        )
        self._update_annotation()

    def _build_frame(self) -> np.ndarray:
        data = np.zeros((self.simulation.grid.height, self.simulation.grid.width), dtype=int)
        for y in range(self.simulation.grid.height):
            for x in range(self.simulation.grid.width):
                state = self.simulation.grid.get_state(x, y)
                value = state
                trail = self.simulation.grid.get_trail(x, y)
                if trail is not None:
                    value = self._trail_indices.get(trail, value)
                data[y, x] = value

        for ant in self.simulation.ants:
            index = self._active_indices[ant.ant_id]
            data[ant.y, ant.x] = index
        return data

    def _update(self, _frame_index: int) -> List[plt.Artist]:
        if self._steps_remaining is None:
            steps_to_run = self.steps_per_frame
        else:
            if self._steps_remaining <= 0:
                steps_to_run = 0
            else:
                steps_to_run = min(self.steps_per_frame, self._steps_remaining)

        for _ in range(steps_to_run):
            self.simulation.step()
            if self._steps_remaining is not None:
                self._steps_remaining -= 1
        frame = self._build_frame()
        self._image.set_data(frame)
        self._update_annotation()
        return [self._image]

    def create_animation(self, steps: int | None = None) -> FuncAnimation:
        """Create a FuncAnimation for the current simulation."""
        if steps is not None and steps < 0:
            msg = "steps must be non-negative"
            raise ValueError(msg)
        self._steps_remaining = steps
        if steps is not None:
            frames = max(0, (steps + self.steps_per_frame - 1) // self.steps_per_frame)
        else:
            frames = None
        animation = FuncAnimation(
            self._figure,
            self._update,
            frames=frames,
            interval=self.frame_interval_ms,
            blit=False,
            repeat=steps is None,
        )
        if getattr(animation, "_save_count", 0) == 0:  # pragma: no cover - attribute contract
            animation._save_count = 1
        return animation

    def _update_annotation(self) -> None:
        topology_label = self._topology_label()
        self._annotation.set_text(
            f"steps: {self.simulation.steps_executed}\ntopology: {topology_label}"
        )

    def _topology_label(self) -> str:
        topo_name = self.simulation.topology.__class__.__name__
        if topo_name.endswith("Topology"):
            topo_name = topo_name[:-8]
        return topo_name.lower()

    def run(
        self,
        steps: int | None = None,
        *,
        show: bool = True,
        save_path: str | None = None,
        save_kwargs: dict | None = None,
    ) -> FuncAnimation:
        """Create an animation, optionally save it, and optionally show it."""

        animation = self.create_animation(steps)
        if save_path:
            animation.save(save_path, **(save_kwargs or {}))
        if show:
            plt.show()
        return animation


def run_matplotlib(
    simulation: Simulation,
    *,
    steps: int | None = None,
    interval_ms: int = 100,
    steps_per_frame: int = 1,
    show: bool = True,
    save_path: str | None = None,
    save_kwargs: dict | None = None,
) -> FuncAnimation:
    """Convenience helper to spin up and optionally persist a Matplotlib animation."""

    animator = MatplotlibAnimator(
        simulation=simulation,
        frame_interval_ms=interval_ms,
        steps_per_frame=steps_per_frame,
    )
    return animator.run(
        steps,
        show=show,
        save_path=save_path,
        save_kwargs=save_kwargs,
    )
