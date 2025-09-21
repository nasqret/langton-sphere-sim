from __future__ import annotations

from ant.core.direction import Heading
from ant.core.simulation import Ant, Simulation
from ant.renderers import AsciiRenderer


def test_ascii_renderer_without_color() -> None:
    ant = Ant(ant_id=1, x=1, y=1, heading=Heading.NORTH, trail_color="red")
    sim = Simulation(width=3, height=3, ants=[ant])
    sim.step()

    render = AsciiRenderer(use_color=False).render(sim)
    lines = render.splitlines()
    assert lines[0] == "steps=1"
    # Row y=1 should contain the trail mark followed by the ant's heading arrow
    assert lines[2].split() == ["_", ".", ">"]


def test_ascii_renderer_with_color_codes() -> None:
    ant = Ant(ant_id=1, x=0, y=0, heading=Heading.NORTH, trail_color="green")
    sim = Simulation(width=2, height=2, ants=[ant])
    render = AsciiRenderer(use_color=True).render(sim)
    assert "\033" in render
