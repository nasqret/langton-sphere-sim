"""ASCII renderer for Langton ant simulations."""
from __future__ import annotations

from typing import Dict, Tuple

from ant.core.direction import Heading
from ant.core.simulation import Simulation

_ANSI_COLORS: Dict[str, str] = {
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    "gray": "90",
    "bright_red": "91",
    "bright_green": "92",
    "bright_yellow": "93",
    "bright_blue": "94",
    "bright_magenta": "95",
    "bright_cyan": "96",
}

_HEADING_SYMBOL = {
    Heading.NORTH: "^",
    Heading.EAST: ">",
    Heading.SOUTH: "v",
    Heading.WEST: "<",
}


class AsciiRenderer:
    """Renders simulation state as a grid of ASCII characters."""

    def __init__(self, use_color: bool = True) -> None:
        self.use_color = use_color

    def render(self, simulation: Simulation) -> str:
        ant_positions: Dict[Tuple[int, int], int] = {
            (ant.x, ant.y): ant.ant_id for ant in simulation.ants
        }
        ant_by_id = {ant.ant_id: ant for ant in simulation.ants}

        lines = [f"steps={simulation.steps_executed}"]
        for y in range(simulation.grid.height):
            cells = []
            for x in range(simulation.grid.width):
                symbol = "_"
                color_code: str | None = None
                if (x, y) in ant_positions:
                    ant_id = ant_positions[(x, y)]
                    ant = ant_by_id[ant_id]
                    symbol = _HEADING_SYMBOL[ant.heading]
                    color_code = self._color_code(ant.trail_color)
                else:
                    trail_id = simulation.grid.get_trail(x, y)
                    if trail_id is not None:
                        ant = ant_by_id.get(trail_id)
                        symbol = "."
                        if ant is not None:
                            color_code = self._color_code(ant.trail_color)
                cells.append(self._apply_color(symbol, color_code))
            lines.append(" ".join(cells))
        return "\n".join(lines)

    def _color_code(self, color_name: str) -> str | None:
        return _ANSI_COLORS.get(color_name.lower())

    def _apply_color(self, symbol: str, color_code: str | None) -> str:
        if not self.use_color or not color_code:
            return symbol
        return f"\033[{color_code}m{symbol}\033[0m"
