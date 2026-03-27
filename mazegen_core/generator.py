from __future__ import annotations

from maze.encoder import write_output
from maze.generator import generate_maze
from maze.grid import Coord, Grid, create_grid
from maze.pattern import stamp_42_pattern
from maze.solver import solve_maze


class MazeGenerator:
    """Reusable wrapper around the project's existing maze generation logic."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
        entry: Coord = (0, 0),
        exit_: Coord | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.entry = entry
        self.exit = exit_ if exit_ is not None else (width - 1, height - 1)

    def create_grid(self) -> Grid:
        return create_grid(self.width, self.height)

    def generate(self) -> tuple[Grid, str, set[Coord]]:
        grid = self.create_grid()
        forbidden = stamp_42_pattern(grid)
        generate_maze(
            grid=grid,
            seed=self.seed,
            perfect=self.perfect,
            forbidden=forbidden,
        )
        path = solve_maze(grid, self.entry, self.exit)
        return grid, path, forbidden

    def write_output(self, output_file: str, grid: Grid, path: str) -> None:
        write_output(output_file, grid, self.entry, self.exit, path)
