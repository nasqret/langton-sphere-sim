"""Non-orientable topology implementations."""
from __future__ import annotations

from ant.topology.base import Coordinates, Topology


class KleinBottleTopology(Topology):
    """Wraps vertically with a horizontal mirror, horizontally like a torus."""

    def wrap(self, x: int, y: int) -> Coordinates:
        new_x = x % self.width
        new_y = y

        while new_y < 0:
            new_y += self.height
            new_x = self._mirror(new_x)
        while new_y >= self.height:
            new_y -= self.height
            new_x = self._mirror(new_x)

        new_x %= self.width
        return Coordinates(new_x, new_y)

    def _mirror(self, x: int) -> int:
        x %= self.width
        return self.width - 1 - x


class ProjectivePlaneTopology(Topology):
    """Wraps both axes with mirroring to emulate the projective plane."""

    def wrap(self, x: int, y: int) -> Coordinates:
        new_x = x
        new_y = y

        while new_y < 0:
            new_y += self.height
            new_x = self._mirror_x(new_x)
        while new_y >= self.height:
            new_y -= self.height
            new_x = self._mirror_x(new_x)

        while new_x < 0:
            new_x += self.width
            new_y = self._mirror_y(new_y)
        while new_x >= self.width:
            new_x -= self.width
            new_y = self._mirror_y(new_y)

        new_x %= self.width
        new_y %= self.height
        return Coordinates(new_x, new_y)

    def _mirror_x(self, x: int) -> int:
        x %= self.width
        return self.width - 1 - x

    def _mirror_y(self, y: int) -> int:
        y %= self.height
        return self.height - 1 - y
