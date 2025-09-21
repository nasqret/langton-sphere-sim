from __future__ import annotations

import argparse

import pytest

from ant.cli import (
    _build_save_kwargs,
    _run_mpl_backend,
    build_ants,
    build_parser,
    make_topology,
    parse_ant_spec,
)
from ant.core.direction import Heading
from ant.core.simulation import Ant, Simulation
from ant.topology import (
    KleinBottleTopology,
    ProjectivePlaneTopology,
    SphereAdjacentPairsTopology,
    TorusTopology,
)


def test_parse_ant_spec_roundtrip() -> None:
    ant = parse_ant_spec("3,4,west,magenta", ant_id=5)
    assert ant == Ant(ant_id=5, x=3, y=4, heading=Heading.WEST, trail_color="magenta")


def test_parse_ant_spec_invalid_heading() -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        parse_ant_spec("0,0,north-east,red", ant_id=1)


def test_build_ants_from_specs() -> None:
    ants = build_ants(["0,0,north,red", "1,1,south,blue"], width=5, height=5)
    assert [ant.ant_id for ant in ants] == [1, 2]
    assert ants[1].heading == Heading.SOUTH


def test_build_ants_default_positions() -> None:
    ants = build_ants(None, width=10, height=10)
    assert len(ants) == 2
    assert ants[0].heading == Heading.NORTH
    assert ants[1].heading == Heading.EAST


def test_make_topology_dispatch() -> None:
    assert isinstance(make_topology("torus", 4, 4), TorusTopology)
    assert isinstance(make_topology("klein", 4, 4), KleinBottleTopology)
    assert isinstance(make_topology("projective", 4, 4), ProjectivePlaneTopology)
    assert isinstance(make_topology("sphere_diag", 4, 4), SphereAdjacentPairsTopology)


def test_parser_rejects_negative_values() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--width", "-1"])


def test_parser_sets_backend_default() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    assert args.backend == "ascii"


def test_parser_accepts_trail_lifetime() -> None:
    parser = build_parser()
    args = parser.parse_args(["--trail-lifetime", "5"])
    assert args.trail_lifetime == 5


def test_parser_accepts_steps_per_frame() -> None:
    parser = build_parser()
    args = parser.parse_args(["--steps-per-frame", "4"])
    assert args.steps_per_frame == 4


def test_run_mpl_backend_invokes_animator(monkeypatch, tmp_path) -> None:
    class DummyAnimator:
        def __init__(self, simulation, frame_interval_ms, figure_size=None, steps_per_frame=1):
            self.simulation = simulation
            self.frame_interval_ms = frame_interval_ms
            self.figure_size = figure_size
            self.steps_per_frame = steps_per_frame
            DummyAnimator.init_kwargs = {
                "frame_interval_ms": frame_interval_ms,
                "steps_per_frame": steps_per_frame,
            }

        def run(self, *, steps, show, save_path, save_kwargs):  # type: ignore[override]
            DummyAnimator.called_with = {
                "steps": steps,
                "show": show,
                "save_path": save_path,
                "save_kwargs": save_kwargs,
            }

    monkeypatch.setattr("ant.cli._load_matplotlib_animator", lambda: DummyAnimator)
    monkeypatch.setattr(
        "ant.cli._build_save_kwargs", lambda args, parser: {"writer": "pillow", "fps": 12}
    )

    parser = build_parser()
    args = parser.parse_args(
        [
            "--backend",
            "mpl",
            "--interval",
            "0.1",
            "--steps",
            "5",
            "--steps-per-frame",
            "3",
            "--save-path",
            str(tmp_path / "anim.gif"),
            "--no-show",
        ]
    )
    ants = build_ants(None, width=6, height=6)
    simulation = Simulation(width=6, height=6, ants=ants)

    _run_mpl_backend(simulation, args, parser)
    assert DummyAnimator.called_with == {
        "steps": 5,
        "show": False,
        "save_path": str(tmp_path / "anim.gif"),
        "save_kwargs": {"writer": "pillow", "fps": 12},
    }
    assert DummyAnimator.init_kwargs["steps_per_frame"] == 3


def test_build_save_kwargs_infers_extension(monkeypatch, tmp_path) -> None:
    parser = build_parser()
    captured = {}

    def fake_resolve(fmt: str) -> str:
        captured["format"] = fmt
        return "pillow"

    monkeypatch.setattr("ant.cli._resolve_writer", fake_resolve)

    args = argparse.Namespace(
        save_path=str(tmp_path / "demo.GIF"),
        save_format=None,
        save_fps=None,
        save_writer=None,
    )

    kwargs = _build_save_kwargs(args, parser)
    assert kwargs == {"writer": "pillow", "fps": 15}
    assert captured["format"] == "gif"


def test_build_save_kwargs_uses_explicit_format(monkeypatch, tmp_path) -> None:
    parser = build_parser()
    monkeypatch.setattr("ant.cli._resolve_writer", lambda fmt: "ffmpeg")
    args = argparse.Namespace(
        save_path=str(tmp_path / "demo"),
        save_format="mp4",
        save_fps=None,
        save_writer=None,
    )
    kwargs = _build_save_kwargs(args, parser)
    assert kwargs == {"writer": "ffmpeg", "fps": 30}


def test_build_save_kwargs_accepts_custom_fps(monkeypatch, tmp_path) -> None:
    parser = build_parser()
    monkeypatch.setattr("ant.cli._resolve_writer", lambda fmt: "pillow")
    args = argparse.Namespace(
        save_path=str(tmp_path / "demo.gif"),
        save_format=None,
        save_fps=24,
        save_writer=None,
    )
    kwargs = _build_save_kwargs(args, parser)
    assert kwargs == {"writer": "pillow", "fps": 24}


def test_build_save_kwargs_errors_without_format(monkeypatch, tmp_path) -> None:
    parser = build_parser()
    args = argparse.Namespace(
        save_path=str(tmp_path / "demo"),
        save_format=None,
        save_fps=None,
        save_writer=None,
    )

    with pytest.raises(SystemExit):
        _build_save_kwargs(args, parser)


def test_build_save_kwargs_accepts_explicit_writer(monkeypatch, tmp_path) -> None:
    parser = build_parser()

    monkeypatch.setattr("matplotlib.animation.writers.is_available", lambda name: name == "imagemagick")

    args = argparse.Namespace(
        save_path=str(tmp_path / "demo"),
        save_format=None,
        save_fps=None,
        save_writer="imagemagick",
    )

    kwargs = _build_save_kwargs(args, parser)
    assert kwargs == {"writer": "imagemagick", "fps": 15}


def test_build_save_kwargs_errors_on_missing_writer(monkeypatch, tmp_path) -> None:
    parser = build_parser()

    monkeypatch.setattr("matplotlib.animation.writers.is_available", lambda name: False)

    args = argparse.Namespace(
        save_path=str(tmp_path / "demo.gif"),
        save_format=None,
        save_fps=None,
        save_writer="imaginary",
    )

    with pytest.raises(SystemExit):
        _build_save_kwargs(args, parser)
