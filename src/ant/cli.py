"""Command-line entry point for running the Langton ant simulator."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from ant.core.direction import Heading
from ant.core.simulation import Ant, Simulation
from ant.renderers import AsciiRenderer, LiveAsciiRunner
from ant.topology import (
    SphereAdjacentPairsTopology,
    KleinBottleTopology,
    ProjectivePlaneTopology,
    TorusTopology,
    Topology,
)

_TOPOLOGY_MAP = {
    "torus": TorusTopology,
    "klein": KleinBottleTopology,
    "projective": ProjectivePlaneTopology,
    "sphere_diag": SphereAdjacentPairsTopology,
}


def _positive_int(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        msg = "value must be a positive integer"
        raise argparse.ArgumentTypeError(msg)
    return ivalue


def _non_negative_int(value: str) -> int:
    ivalue = int(value)
    if ivalue < 0:
        msg = "value must be a non-negative integer"
        raise argparse.ArgumentTypeError(msg)
    return ivalue


def _non_negative_float(value: str) -> float:
    fvalue = float(value)
    if fvalue < 0:
        msg = "value must be a non-negative float"
        raise argparse.ArgumentTypeError(msg)
    return fvalue


def parse_ant_spec(spec: str, *, ant_id: int) -> Ant:
    """Parse a single ant descriptor of the form ``x,y,heading,color``."""
    parts = [value.strip() for value in spec.split(",")]
    if len(parts) != 4:
        msg = (
            "Ant specification must contain x,y,heading,color. "
            f"Received: '{spec}'."
        )
        raise argparse.ArgumentTypeError(msg)
    try:
        x = int(parts[0])
        y = int(parts[1])
    except ValueError as exc:  # pragma: no cover - defensive
        msg = f"Ant coordinates must be integers: '{spec}'."
        raise argparse.ArgumentTypeError(msg) from exc

    heading_key = parts[2].upper()
    try:
        heading = Heading[heading_key]
    except KeyError as exc:
        msg = f"Unknown heading '{parts[2]}'. Expected one of: {', '.join(h.name for h in Heading)}"
        raise argparse.ArgumentTypeError(msg) from exc

    color = parts[3]
    return Ant(ant_id=ant_id, x=x, y=y, heading=heading, trail_color=color)


def build_ants(specs: Iterable[str] | None, width: int, height: int) -> List[Ant]:
    if specs:
        return [parse_ant_spec(spec, ant_id=index + 1) for index, spec in enumerate(specs)]

    mid_x = width // 2
    mid_y = height // 2
    return [
        Ant(ant_id=1, x=mid_x, y=mid_y, heading=Heading.NORTH, trail_color="red"),
        Ant(ant_id=2, x=(mid_x + 1) % width, y=mid_y, heading=Heading.EAST, trail_color="cyan"),
    ]


def make_topology(name: str, width: int, height: int) -> Topology:
    try:
        topology_cls = _TOPOLOGY_MAP[name]
    except KeyError as exc:  # pragma: no cover - argparse validates choices
        msg = f"Unsupported topology '{name}'"
        raise ValueError(msg) from exc
    return topology_cls(width, height)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Langton ant simulator")
    parser.add_argument("--width", type=_positive_int, default=40, help="Grid width")
    parser.add_argument("--height", type=_positive_int, default=20, help="Grid height")
    parser.add_argument(
        "--topology",
        choices=sorted(_TOPOLOGY_MAP.keys()),
        default="torus",
        help="Surface topology",
    )
    parser.add_argument(
        "--backend",
        choices=["ascii", "mpl"],
        default="ascii",
        help="Rendering backend to use",
    )
    parser.add_argument(
        "--steps",
        type=_non_negative_int,
        default=200,
        help="Number of steps to simulate (initial frame always rendered)",
    )
    parser.add_argument(
        "--interval",
        type=_non_negative_float,
        default=0.05,
        help="Delay between frames in seconds",
    )
    parser.add_argument(
        "--steps-per-frame",
        type=_positive_int,
        default=1,
        help="Simulation steps to compute between rendered frames",
    )
    parser.add_argument(
        "--trail-lifetime",
        type=_non_negative_int,
        default=20,
        help="Number of steps a trail remains visible",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Render without ANSI colors",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Do not clear the terminal between frames",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not open the Matplotlib window (mpl backend only)",
    )
    parser.add_argument(
        "--save-path",
        default=None,
        help="File path to save the Matplotlib animation (mpl backend only)",
    )
    parser.add_argument(
        "--save-format",
        choices=["gif", "mp4"],
        default=None,
        help="Force animation format; inferred from --save-path extension when omitted",
    )
    parser.add_argument(
        "--save-fps",
        type=_positive_int,
        default=None,
        help="Frames per second when saving animations (mpl backend)",
    )
    parser.add_argument(
        "--save-writer",
        default=None,
        help="Explicit Matplotlib writer (e.g., pillow, imagemagick, ffmpeg)",
    )
    parser.add_argument(
        "--ant",
        dest="ant_specs",
        action="append",
        metavar="SPEC",
        help="Ant spec formatted as x,y,heading,color. Can be repeated.",
    )
    return parser


def _load_matplotlib_animator():
    from ant.renderers.mpl import MatplotlibAnimator

    return MatplotlibAnimator


def _infer_format(save_path: str) -> str | None:
    suffix = Path(save_path).suffix.lower()
    if suffix.startswith("."):
        suffix = suffix[1:]
    return suffix or None


_FORMAT_WRITERS = {
    "gif": ["pillow", "imagemagick", "imagemagick_file"],
    "mp4": ["ffmpeg", "ffmpeg_file"],
}

_WRITER_HINTS = {
    "gif": "Install ImageMagick (`brew install imagemagick`) or ensure Pillow support is available.",
    "mp4": "Install FFmpeg (`brew install ffmpeg`) to enable MP4 writing.",
}


def _resolve_writer(save_format: str) -> str:
    from matplotlib.animation import writers

    candidates = _FORMAT_WRITERS.get(save_format)
    if not candidates:
        raise RuntimeError(f"Unsupported save format '{save_format}'.")
    for candidate in candidates:
        if writers.is_available(candidate):
            return candidate
    raise RuntimeError(
        f"No available Matplotlib writer for format '{save_format}'. Install one of: {', '.join(candidates)}."
    )


def _build_save_kwargs(args: argparse.Namespace, parser: argparse.ArgumentParser) -> dict | None:
    if not args.save_path:
        return None

    save_format = args.save_format or _infer_format(args.save_path)
    writer_name = args.save_writer

    if writer_name:
        from matplotlib.animation import writers

        if not writers.is_available(writer_name):
            hint = _writer_hint_for(writer_name)
            parser.error(
                f"Matplotlib writer '{writer_name}' is not available. {hint}"
            )
    else:
        if not save_format:
            parser.error("Specify --save-format or provide a file extension in --save-path.")
        try:
            writer_name = _resolve_writer(save_format)
        except RuntimeError as exc:  # pragma: no cover - depends on local writers
            hint = _writer_hint_for(save_format)
            parser.error(f"{exc}. {hint}")

    if not save_format:
        save_format = _infer_format_from_writer(writer_name)

    fps = args.save_fps
    if fps is None:
        fps = _default_fps_for_format(save_format)

    kwargs: dict[str, object] = {"writer": writer_name, "fps": fps}
    return kwargs


def _infer_format_from_writer(writer: str | None) -> str:
    if not writer:
        return "gif"
    writer = writer.lower()
    if "ffmpeg" in writer:
        return "mp4"
    if "gif" in writer or "mage" in writer or "pillow" in writer:
        return "gif"
    return "gif"


def _default_fps_for_format(save_format: str | None) -> int:
    if save_format == "mp4":
        return 30
    return 15


def _writer_hint_for(key: str | None) -> str:
    if not key:
        return "Install ImageMagick or FFmpeg, or choose an available writer with --save-writer."
    key = key.lower()
    if key in _WRITER_HINTS:
        return _WRITER_HINTS[key]
    if "ffmpeg" in key:
        return _WRITER_HINTS["mp4"]
    if "mage" in key or "gif" in key or "pillow" in key:
        return _WRITER_HINTS["gif"]
    return "Install the required writer backend or select another via --save-writer."


def _run_mpl_backend(simulation: Simulation, args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    try:
        animator_cls = _load_matplotlib_animator()
    except ImportError:  # pragma: no cover - optional dependency
        parser.error(
            "Matplotlib backend requires optional dependency 'matplotlib'. "
            "Install with `pip install .[viz]`."
        )

    interval_ms = max(0, int(args.interval * 1000))
    animator = animator_cls(
        simulation,
        frame_interval_ms=interval_ms,
        steps_per_frame=args.steps_per_frame,
    )
    save_kwargs = _build_save_kwargs(args, parser)
    animator.run(
        steps=args.steps,
        show=not args.no_show,
        save_path=args.save_path,
        save_kwargs=save_kwargs,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    ants = build_ants(args.ant_specs, args.width, args.height)
    topology = make_topology(args.topology, args.width, args.height)
    simulation = Simulation(
        width=args.width,
        height=args.height,
        ants=ants,
        topology=topology,
        trail_lifetime=args.trail_lifetime,
    )
    if args.backend == "ascii":
        renderer = AsciiRenderer(use_color=not args.no_color)
        runner = LiveAsciiRunner(
            simulation,
            renderer=renderer,
            interval=args.interval,
            clear_screen=not args.no_clear,
            steps_per_frame=args.steps_per_frame,
        )
        runner.run(total_steps=args.steps)
    else:
        _run_mpl_backend(simulation, args, parser)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
