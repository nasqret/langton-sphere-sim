"""Simulation engine for Langton ants."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from ant.core.direction import Heading, heading_to_step
from ant.core.grid import Grid
from ant.topology.base import Coordinates, Topology, TorusTopology


@dataclass
class Ant:
    """Stateful Langton ant."""

    ant_id: int
    x: int
    y: int
    heading: Heading
    trail_color: str

    def position(self) -> Coordinates:
        return Coordinates(self.x, self.y)


class Simulation:
    """Coordinates multiple Langton ants on a shared grid."""

    def __init__(
        self,
        width: int,
        height: int,
        ants: Sequence[Ant],
        topology: Topology | None = None,
        trail_lifetime: int = 20,
    ) -> None:
        self.grid = Grid(width=width, height=height)
        self.topology = topology or TorusTopology(width, height)
        if len({ant.ant_id for ant in ants}) != len(ants):
            msg = "Ant IDs must be unique"
            raise ValueError(msg)
        self.ants: List[Ant] = list(ants)
        self.steps_executed = 0
        if trail_lifetime < 0:
            msg = "trail_lifetime must be non-negative"
            raise ValueError(msg)
        self.trail_lifetime = trail_lifetime

    def step(self) -> None:
        for ant in self.ants:
            self._apply_rules(ant)
        self.steps_executed += 1
        self.grid.decay_trails()

    def run(self, steps: int) -> None:
        if steps < 0:
            msg = "Steps must be non-negative"
            raise ValueError(msg)
        for _ in range(steps):
            self.step()

    def _apply_rules(self, ant: Ant) -> None:
        state = self.grid.get_state(ant.x, ant.y)
        if state == 0:
            ant.heading = ant.heading.turn_right()
        else:
            ant.heading = ant.heading.turn_left()
        self.grid.flip_state(ant.x, ant.y)
        self.grid.mark_trail(ant.x, ant.y, ant.ant_id, self.trail_lifetime)
        step_vec = heading_to_step(ant.heading)
        wrapped = self.topology.wrap(ant.x + step_vec.dx, ant.y + step_vec.dy)
        ant.x, ant.y = wrapped.x, wrapped.y

    def ants_positions(self) -> List[Coordinates]:
        return [ant.position() for ant in self.ants]

    def ant_by_id(self, ant_id: int) -> Ant:
        for ant in self.ants:
            if ant.ant_id == ant_id:
                return ant
        msg = f"Unknown ant id {ant_id}"
        raise KeyError(msg)
