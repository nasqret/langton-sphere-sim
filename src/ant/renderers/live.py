"""Live terminal runner built on top of the ASCII renderer."""
from __future__ import annotations

import sys
import time
from io import TextIOBase
from typing import Optional

from ant.core.simulation import Simulation
from ant.renderers.ascii import AsciiRenderer

_CLEAR_SEQUENCE = "\033[2J\033[H"


class LiveAsciiRunner:
    """Streams simulation frames to a terminal-like target."""

    def __init__(
        self,
        simulation: Simulation,
        renderer: Optional[AsciiRenderer] = None,
        *,
        interval: float = 0.1,
        clear_screen: bool = True,
        stream: Optional[TextIOBase] = None,
        steps_per_frame: int = 1,
    ) -> None:
        if interval < 0:
            msg = "interval must be non-negative"
            raise ValueError(msg)
        if steps_per_frame <= 0:
            msg = "steps_per_frame must be a positive integer"
            raise ValueError(msg)
        self.simulation = simulation
        self.renderer = renderer or AsciiRenderer()
        self.interval = interval
        self.clear_screen = clear_screen
        self.stream = stream or sys.stdout
        self.steps_per_frame = steps_per_frame

    def run(self, total_steps: Optional[int] = None) -> None:
        """Render continuously, rendering once per batch of simulation steps."""

        if total_steps is not None and total_steps < 0:
            msg = "total_steps must be non-negative"
            raise ValueError(msg)

        remaining = total_steps
        self._emit_frame()
        while True:
            if remaining is not None:
                if remaining == 0:
                    break
                steps_this_frame = min(self.steps_per_frame, remaining)
                remaining -= steps_this_frame
            else:
                steps_this_frame = self.steps_per_frame

            for _ in range(steps_this_frame):
                self.simulation.step()
            if self.interval:
                time.sleep(self.interval)
            self._emit_frame()

    def _emit_frame(self) -> None:
        frame = self.renderer.render(self.simulation)
        if self.clear_screen:
            self.stream.write(_CLEAR_SEQUENCE)
        self.stream.write(frame)
        self.stream.write("\n")
        self.stream.flush()
