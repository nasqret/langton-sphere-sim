from __future__ import annotations

import pytest

from ant.core.direction import Heading
from ant.core.simulation import Ant, Simulation
from ant.topology.nonorientable import KleinBottleTopology, ProjectivePlaneTopology


@pytest.fixture
def single_ant_sim() -> Simulation:
    ant = Ant(ant_id=1, x=1, y=1, heading=Heading.NORTH, trail_color="red")
    return Simulation(width=3, height=3, ants=[ant])


def test_single_step_flips_cell_and_moves(single_ant_sim: Simulation) -> None:
    sim = single_ant_sim
    sim.step()

    # Cell flipped to black
    assert sim.grid.get_state(1, 1) == 1
    # Ant turned right (east) and moved one step
    ant = sim.ant_by_id(1)
    assert ant.heading == Heading.EAST
    assert (ant.x, ant.y) == (2, 1)
    # Trail recorded
    assert sim.grid.get_trail(1, 1) == 1


def test_wraps_on_torus_boundary() -> None:
    ant = Ant(ant_id=7, x=0, y=0, heading=Heading.WEST, trail_color="blue")
    sim = Simulation(width=4, height=4, ants=[ant])
    sim.step()
    ant = sim.ant_by_id(7)
    assert (ant.x, ant.y) == (0, 3)
    assert sim.grid.get_state(0, 0) == 1


def test_multiple_ants_share_grid() -> None:
    ants = [
        Ant(ant_id=1, x=0, y=0, heading=Heading.NORTH, trail_color="green"),
        Ant(ant_id=2, x=1, y=0, heading=Heading.NORTH, trail_color="yellow"),
    ]
    sim = Simulation(width=3, height=3, ants=ants)
    sim.step()

    # Both ants should have flipped their starting cells and moved
    assert sim.grid.get_state(0, 0) == 1
    assert sim.grid.get_state(1, 0) == 1
    assert sim.grid.get_trail(0, 0) == 1
    assert sim.grid.get_trail(1, 0) == 2

    positions = sorted((ant.x, ant.y) for ant in sim.ants)
    assert positions == [(1, 0), (2, 0)]


def test_simulation_with_klein_topology_wraps_with_mirror() -> None:
    ant = Ant(ant_id=9, x=1, y=0, heading=Heading.WEST, trail_color="purple")
    topo = KleinBottleTopology(5, 4)
    sim = Simulation(width=5, height=4, ants=[ant], topology=topo)
    sim.step()
    ant = sim.ant_by_id(9)
    assert (ant.x, ant.y) == (3, 3)


def test_simulation_with_projective_topology_wraps_both_axes() -> None:
    ant = Ant(ant_id=11, x=0, y=1, heading=Heading.NORTH, trail_color="cyan")
    topo = ProjectivePlaneTopology(4, 4)
    sim = Simulation(width=4, height=4, ants=[ant], topology=topo)
    sim.grid.set_state(0, 1, 1)
    sim.step()
    ant = sim.ant_by_id(11)
    assert (ant.x, ant.y) == (3, 2)


def test_trail_fades_after_lifetime() -> None:
    ant = Ant(ant_id=5, x=1, y=1, heading=Heading.NORTH, trail_color="red")
    sim = Simulation(width=3, height=3, ants=[ant], trail_lifetime=2)

    sim.step()
    assert sim.grid.get_trail(1, 1) == 5

    sim.step()
    assert sim.grid.get_trail(1, 1) is None
