"""Orientable topology implementations."""
from __future__ import annotations

from ant.topology.base import Coordinates, Topology


class SphereAdjacentPairsTopology(Topology):
    """Sphere via adjacent-edge identifications on a square grid."""

    def __init__(self, width: int, height: int) -> None:
        super().__init__(width, height)
        if width != height:
            msg = "SphereAdjacentPairsTopology requires width == height"
            raise ValueError(msg)
        if width < 2:
            msg = "SphereAdjacentPairsTopology requires grid size >= 2"
            raise ValueError(msg)

    def wrap(self, x: int, y: int) -> Coordinates:
        n = self.width

        u = x
        v = y

        while not (0 <= u <= n - 1 and 0 <= v <= n - 1):
            if v < 0:
                t = self._mirror_fold(u, n - 1)
                u, v = 0, t
                continue
            if u < 0:
                t = self._mirror_fold(v, n - 1)
                u, v = t, 0
                continue
            if v > n - 1:
                t = self._mirror_fold(u, n - 1)
                u, v = n - 1, (n - 1) - t
                continue
            if u > n - 1:
                t = self._mirror_fold(v, n - 1)
                u, v = (n - 1) - t, n - 1
                continue

        return Coordinates(u, v)

    @staticmethod
    def _mirror_fold(t: int, n: int) -> int:
        if n <= 0:
            return 0
        period = 2 * n
        r = t % period
        if r < 0:
            r += period
        return r if r <= n else 2 * n - r
