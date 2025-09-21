"""Grid state for Langton ant simulation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


CellState = int  # 0 for white, 1 for black
TrailId = Optional[int]
TrailData = Optional[Tuple[int, int]]  # (ant_id, remaining lifetime)


@dataclass
class Grid:
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            msg = "Width and height must be positive integers"
            raise ValueError(msg)
        self._cells: List[List[CellState]] = [
            [0 for _ in range(self.width)] for _ in range(self.height)
        ]
        self._trail: List[List[TrailData]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

    def get_state(self, x: int, y: int) -> CellState:
        return self._cells[y][x]

    def flip_state(self, x: int, y: int) -> CellState:
        self._cells[y][x] ^= 1
        return self._cells[y][x]

    def set_state(self, x: int, y: int, state: CellState) -> None:
        self._cells[y][x] = state

    def mark_trail(self, x: int, y: int, trail_id: int, lifetime: int) -> None:
        self._trail[y][x] = (trail_id, lifetime)

    def get_trail(self, x: int, y: int) -> TrailId:
        data = self._trail[y][x]
        if not data:
            return None
        trail_id, ttl = data
        if ttl <= 0:
            return None
        return trail_id

    def decay_trails(self) -> None:
        for y in range(self.height):
            row = self._trail[y]
            for x in range(self.width):
                data = row[x]
                if data is None:
                    continue
                trail_id, ttl = data
                if ttl <= 1:
                    row[x] = None
                else:
                    row[x] = (trail_id, ttl - 1)

    @property
    def cells(self) -> List[List[CellState]]:
        return self._cells

    @property
    def trails(self) -> List[List[TrailId]]:
        return [[self.get_trail(x, y) for x in range(self.width)] for y in range(self.height)]
