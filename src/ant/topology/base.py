"""Topology abstractions for Langton ant simulations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Coordinates:
    """Immutable integer coordinates on the grid."""

    x: int
    y: int


class Topology(ABC):
    """Defines how positions wrap when leaving grid bounds."""

    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            msg = "Width and height must be positive integers"
            raise ValueError(msg)
        self.width = width
        self.height = height

    @abstractmethod
    def wrap(self, x: int, y: int) -> Coordinates:
        """Return new coordinates after applying topology wrapping."""


class TorusTopology(Topology):
    """Wraps both axes modulo the grid size (classic torus)."""

    def wrap(self, x: int, y: int) -> Coordinates:
        return Coordinates(x % self.width, y % self.height)
