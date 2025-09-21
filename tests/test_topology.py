from __future__ import annotations

import pytest

from ant.topology.base import TorusTopology
from ant.topology.nonorientable import KleinBottleTopology, ProjectivePlaneTopology
from ant.topology.orientable import SphereAdjacentPairsTopology


def test_torus_wraps_modulo() -> None:
    topo = TorusTopology(5, 4)
    wrapped = topo.wrap(-1, 4)
    assert (wrapped.x, wrapped.y) == (4, 0)


def test_klein_vertical_wrap_mirrors_horizontal() -> None:
    topo = KleinBottleTopology(5, 3)
    wrapped = topo.wrap(1, -1)
    assert (wrapped.x, wrapped.y) == (3, 2)


def test_klein_horizontal_wrap_is_torus() -> None:
    topo = KleinBottleTopology(5, 3)
    wrapped = topo.wrap(5, 1)
    assert (wrapped.x, wrapped.y) == (0, 1)


def test_projective_vertical_wrap() -> None:
    topo = ProjectivePlaneTopology(4, 4)
    wrapped = topo.wrap(1, -1)
    assert (wrapped.x, wrapped.y) == (2, 3)


def test_projective_horizontal_wrap() -> None:
    topo = ProjectivePlaneTopology(4, 4)
    wrapped = topo.wrap(5, 1)
    assert (wrapped.x, wrapped.y) == (1, 2)


def test_projective_multiple_crossings() -> None:
    topo = ProjectivePlaneTopology(4, 4)
    wrapped = topo.wrap(-5, -5)
    assert (wrapped.x, wrapped.y) == (3, 3)


def test_sphere_diagonal_requires_square_grid() -> None:
    with pytest.raises(ValueError):
        SphereAdjacentPairsTopology(1, 4)


def test_sphere_diagonal_reflects_upper_triangle() -> None:
    topo = SphereAdjacentPairsTopology(6, 6)
    wrapped = topo.wrap(5, 6)
    assert (wrapped.x, wrapped.y) == (5, 0)


def test_sphere_diagonal_bottom_reflection() -> None:
    topo = SphereAdjacentPairsTopology(6, 6)
    wrapped = topo.wrap(2, 7)
    assert (wrapped.x, wrapped.y) == (5, 3)


def test_sphere_diagonal_interior_identity() -> None:
    topo = SphereAdjacentPairsTopology(6, 6)
    wrapped = topo.wrap(3, 3)
    assert (wrapped.x, wrapped.y) == (3, 3)


def test_sphere_diagonal_left_to_top() -> None:
    topo = SphereAdjacentPairsTopology(6, 6)
    wrapped = topo.wrap(-2, 2)
    assert (wrapped.x, wrapped.y) == (2, 0)


def test_sphere_diagonal_requires_square_grid() -> None:
    with pytest.raises(ValueError):
        SphereAdjacentPairsTopology(8, 4)
