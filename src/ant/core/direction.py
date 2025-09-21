"""Heading utilities for Langton ants."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Heading(Enum):
    """Cartesian heading with clockwise rotation order."""

    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    @property
    def vector(self) -> tuple[int, int]:
        return self.value

    def turn_right(self) -> "Heading":
        order = [Heading.NORTH, Heading.EAST, Heading.SOUTH, Heading.WEST]
        idx = order.index(self)
        return order[(idx + 1) % len(order)]

    def turn_left(self) -> "Heading":
        order = [Heading.NORTH, Heading.EAST, Heading.SOUTH, Heading.WEST]
        idx = order.index(self)
        return order[(idx - 1) % len(order)]


@dataclass(frozen=True)
class Step:
    """Movement delta."""

    dx: int
    dy: int


def heading_to_step(heading: Heading) -> Step:
    dx, dy = heading.vector
    return Step(dx, dy)
