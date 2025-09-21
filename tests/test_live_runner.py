from __future__ import annotations

import io

from ant.core.direction import Heading
from ant.core.simulation import Ant, Simulation
from ant.renderers import AsciiRenderer
from ant.renderers.live import LiveAsciiRunner


def build_simulation() -> Simulation:
    ants = [
        Ant(ant_id=1, x=0, y=0, heading=Heading.NORTH, trail_color="green"),
    ]
    return Simulation(width=3, height=3, ants=ants)


def test_live_runner_progresses_simulation() -> None:
    sim = build_simulation()
    buffer = io.StringIO()
    runner = LiveAsciiRunner(
        sim,
        renderer=AsciiRenderer(use_color=False),
        interval=0.0,
        clear_screen=False,
        stream=buffer,
        steps_per_frame=1,
    )
    runner.run(total_steps=2)

    output = buffer.getvalue()
    assert output.count("steps=") == 3  # Initial frame + two updates
    assert "steps=2" in output
    assert sim.steps_executed == 2


def test_live_runner_writes_clear_sequence_when_enabled() -> None:
    sim = build_simulation()
    buffer = io.StringIO()
    runner = LiveAsciiRunner(
        sim,
        interval=0.0,
        clear_screen=True,
        stream=buffer,
        steps_per_frame=1,
    )
    runner.run(total_steps=1)
    output = buffer.getvalue()
    assert output.count("\033[2J\033[H") == 2


def test_live_runner_steps_per_frame_controls_progression() -> None:
    sim = build_simulation()
    buffer = io.StringIO()
    runner = LiveAsciiRunner(
        sim,
        renderer=AsciiRenderer(use_color=False),
        interval=0.0,
        clear_screen=False,
        stream=buffer,
        steps_per_frame=3,
    )
    runner.run(total_steps=7)

    assert sim.steps_executed == 7
    # Initial frame + ceil(7/3) updates = 4 frames -> 5 lines with "steps="
    assert buffer.getvalue().count("steps=") == 1 + ((7 + 3 - 1) // 3)
