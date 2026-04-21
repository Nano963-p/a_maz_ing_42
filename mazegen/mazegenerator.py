from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from typing import TypeAlias


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

Coord: TypeAlias = tuple[int, int]
Grid: TypeAlias = list[list["MazeGenerator.Cell"]]
Neighbor: TypeAlias = tuple[int, int, str]
ParentMap: TypeAlias = dict[Coord, tuple[Coord, str] | None]
ForbiddenSet: TypeAlias = set[Coord]

_PATTERN_42_RAW: list[str] = [
    "X X XXX",
    "X X   X",
    "XXX XXX",
    "  X X  ",
    "  X XXX",
]

_PATTERN_HEIGHT: int = len(_PATTERN_42_RAW)
_PATTERN_WIDTH: int = max(len(row) for row in _PATTERN_42_RAW)
_PATTERN_42: list[str] = [
    row.ljust(_PATTERN_WIDTH) for row in _PATTERN_42_RAW
]

MIN_WIDTH: int = _PATTERN_WIDTH + 2
MIN_HEIGHT: int = _PATTERN_HEIGHT + 2


class MazeGenerator:
    """Maze generation, solving, and encoding — all in one class."""

    # ------------------------------------------------------------------
    # Nested Cell
    # ------------------------------------------------------------------

    @dataclass
    class Cell:
        """Represent one maze cell with wall and generation state."""
        north: bool = True
        east: bool = True
        south: bool = True
        west: bool = True
        visited: bool = False

    # ------------------------------------------------------------------
    # Pattern constants (class-level aliases)
    # ------------------------------------------------------------------

    MIN_WIDTH: int = MIN_WIDTH
    MIN_HEIGHT: int = MIN_HEIGHT

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def __init__(
        self,
        width: int,
        height: int,
        seed: str | None = None,
        perfect: bool = True,
        entry: Coord = (0, 0),
        exit_: Coord | None = None,
        draw_pattern: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.entry = entry
        self.exit = exit_ if exit_ is not None else (width - 1, height - 1)
        self.draw_pattern = draw_pattern

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_grid(self) -> Grid:
        """Create a 2D grid of cells with all walls initially closed."""
        return [
            [MazeGenerator.Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def generate(self) -> tuple[Grid, str, ForbiddenSet]:
        """Generate, solve, and return the maze grid, path, and forbidden."""
        grid = self.create_grid()
        if self.draw_pattern:
            forbidden = self._stamp_42_pattern(grid)
        else:
            forbidden = set()
        self._generate_maze(grid, forbidden)
        path = self._solve_maze(grid, self.entry, self.exit)
        return grid, path, forbidden

    def write_output(self, output_file: str, grid: Grid, path: str) -> None:
        """Write the maze output to a file."""
        content = self._format_output(grid, self.entry, self.exit, path)
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(content)

    @staticmethod
    def validate_no_3x3(grid: Grid) -> bool:
        """
        Validate that the maze contains no 3x3 fully open areas.

        Returns True if the maze is valid, False otherwise.
        Prints the coordinates of any violations found.
        """
        height = len(grid)
        width = len(grid[0])
        violations: list[Coord] = []

        for top in range(height - 2):
            for left in range(width - 2):
                open_block = True
                for row in range(top, top + 3):
                    for col in range(left, left + 3):
                        cell = grid[row][col]
                        if col < left + 2 and cell.east:
                            open_block = False
                        if row < top + 2 and cell.south:
                            open_block = False
                if open_block:
                    violations.append((left, top))

        if violations:
            print(
                f"Error: {len(violations)} "
                "forbidden 3x3 open area(s) found at:"
                f"{violations}")
            return False
        return True

    # ------------------------------------------------------------------
    # Grid helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _in_bounds(x: int, y: int, width: int, height: int) -> bool:
        """Return True if the coordinates are inside the grid."""
        return 0 <= x < width and 0 <= y < height

    @staticmethod
    def _get_neighbors(
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> list[Neighbor]:
        """Return all valid neighbors as (nx, ny, direction) tuples."""
        neighbors: list[Neighbor] = []
        if MazeGenerator._in_bounds(x, y - 1, width, height):
            neighbors.append((x, y - 1, "N"))
        if MazeGenerator._in_bounds(x + 1, y, width, height):
            neighbors.append((x + 1, y, "E"))
        if MazeGenerator._in_bounds(x, y + 1, width, height):
            neighbors.append((x, y + 1, "S"))
        if MazeGenerator._in_bounds(x - 1, y, width, height):
            neighbors.append((x - 1, y, "W"))
        return neighbors

    @staticmethod
    def _get_unvisited_neighbors(
        x: int,
        y: int,
        grid: Grid,
        forbidden: ForbiddenSet | None = None,
    ) -> list[Neighbor]:
        """Return neighbors that are unvisited and not forbidden."""
        height = len(grid)
        width = len(grid[0])
        neighbors = MazeGenerator._get_neighbors(x, y, width, height)
        return [
            (nx, ny, direction)
            for nx, ny, direction in neighbors
            if not grid[ny][nx].visited
            and (forbidden is None or (nx, ny) not in forbidden)
        ]

    @staticmethod
    def _get_open_neighbors(x: int, y: int, grid: Grid) -> list[Neighbor]:
        """Return neighbors that are reachable through open walls."""
        height = len(grid)
        width = len(grid[0])
        neighbors: list[Neighbor] = []
        if y > 0 and not grid[y][x].north:
            neighbors.append((x, y - 1, "N"))
        if x < width - 1 and not grid[y][x].east:
            neighbors.append((x + 1, y, "E"))
        if y < height - 1 and not grid[y][x].south:
            neighbors.append((x, y + 1, "S"))
        if x > 0 and not grid[y][x].west:
            neighbors.append((x - 1, y, "W"))
        return neighbors

    @staticmethod
    def _remove_wall_between(
        grid: Grid,
        x: int,
        y: int,
        nx: int,
        ny: int,
    ) -> None:
        """
        Remove the wall between two adjacent cells.

        Both cells are updated so wall data stays coherent.
        Raises ValueError if the cells are not adjacent.
        """
        current = grid[y][x]
        neighbor = grid[ny][nx]

        if nx == x and ny == y - 1:
            current.north = False
            neighbor.south = False
        elif nx == x + 1 and ny == y:
            current.east = False
            neighbor.west = False
        elif nx == x and ny == y + 1:
            current.south = False
            neighbor.north = False
        elif nx == x - 1 and ny == y:
            current.west = False
            neighbor.east = False
        else:
            raise ValueError("Cells are not adjacent.")

    @staticmethod
    def _is_open(grid: Grid, x: int, y: int, direction: str) -> bool:
        """Return True if movement from (x, y) is possible."""
        cell = grid[y][x]
        if direction == "N":
            return not cell.north
        if direction == "E":
            return not cell.east
        if direction == "S":
            return not cell.south
        if direction == "W":
            return not cell.west
        raise ValueError("Invalid direction. Use 'N', 'E', 'S', or 'W'.")

    # ------------------------------------------------------------------
    # Pattern (42)
    # ------------------------------------------------------------------

    @staticmethod
    def _can_draw_42(width: int, height: int) -> bool:
        """Return True if the maze is large enough to fit the 42 pattern."""
        return width >= MIN_WIDTH and height >= MIN_HEIGHT

    @staticmethod
    def _close_cell(grid: Grid, x: int, y: int) -> None:
        """Set all four walls of a cell to closed."""
        cell = grid[y][x]
        cell.north = True
        cell.east = True
        cell.south = True
        cell.west = True

    @staticmethod
    def _pattern_coords(width: int, height: int) -> list[Coord]:
        """Compute centered coordinates for the 42 pattern inside the maze."""
        offset_x = (width - _PATTERN_WIDTH) // 2
        offset_y = (height - _PATTERN_HEIGHT) // 2
        return [
            (offset_x + px, offset_y + py)
            for py, row in enumerate(_PATTERN_42)
            for px, ch in enumerate(row)
            if ch != " "
        ]

    @staticmethod
    def _stamp_42_pattern(grid: Grid) -> ForbiddenSet:
        """
        Stamp the 42 pattern into the grid before maze generation.

        Returns a set of forbidden coordinates corresponding to the 42 pattern.
        Raises ValueError if the grid is empty.
        """
        if not grid or not grid[0]:
            raise ValueError("Maze grid cannot be empty.")

        height = len(grid)
        width = len(grid[0])

        if not MazeGenerator._can_draw_42(width, height):
            print("Error: Maze too small to include the 42 pattern.")
            return set()

        coords = MazeGenerator._pattern_coords(width, height)
        for x, y in coords:
            MazeGenerator._close_cell(grid, x, y)
        return set(coords)

    # ------------------------------------------------------------------
    # Generator (DFS)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_grid(grid: Grid) -> None:
        """Validate that the maze grid is not empty."""
        if not grid or not grid[0]:
            raise ValueError("Maze grid cannot be empty.")

    @staticmethod
    def _pick_start_cell(
        grid: Grid,
        forbidden: ForbiddenSet | None = None,
    ) -> Coord:
        """
        Return a valid starting cell for DFS generation.

        The first available non-forbidden cell is selected.
        Raises ValueError if no valid starting cell exists.
        """
        height = len(grid)
        width = len(grid[0])
        forbidden = forbidden or set()

        for y in range(height):
            for x in range(width):
                if (x, y) not in forbidden:
                    return (x, y)

        raise ValueError(
            "No valid starting cell available outside the 42 pattern."
        )

    @staticmethod
    def _reset_visited(grid: Grid) -> None:
        """Clear the visited flag on every cell after generation."""
        for row in grid:
            for cell in row:
                cell.visited = False

    @staticmethod
    def _dfs_generate(
        grid: Grid,
        rng: random.Random,
        start: Coord,
        forbidden: ForbiddenSet | None = None,
    ) -> None:
        """
        Generate a maze using iterative DFS with backtracking.

        Forbidden cells are never visited and never opened.
        """
        stack: list[Coord] = [start]
        start_x, start_y = start
        grid[start_y][start_x].visited = True

        while stack:
            x, y = stack[-1]
            neighbors = MazeGenerator._get_unvisited_neighbors(
                x,
                y,
                grid,
                forbidden,
            )

            if not neighbors:
                stack.pop()
                continue

            nx, ny, _ = rng.choice(neighbors)
            MazeGenerator._remove_wall_between(grid, x, y, nx, ny)
            grid[ny][nx].visited = True
            stack.append((nx, ny))

    @staticmethod
    def _add_extra_openings(
        grid: Grid,
        rng: random.Random,
        forbidden: ForbiddenSet | None = None,
    ) -> None:
        """Add extra openings to create loops in a non-perfect maze."""
        height = len(grid)
        width = len(grid[0])
        forbidden = forbidden or set()

        for y in range(height):
            for x in range(width):
                if (x, y) in forbidden:
                    continue

                candidates: list[Coord] = []

                if x + 1 < width and (x + 1, y) not in forbidden:
                    if grid[y][x].east and grid[y][x + 1].west:
                        candidates.append((x + 1, y))

                if y + 1 < height and (x, y + 1) not in forbidden:
                    if grid[y][x].south and grid[y + 1][x].north:
                        candidates.append((x, y + 1))

                if candidates and rng.random() < 0.15:
                    nx, ny = rng.choice(candidates)
                    MazeGenerator._remove_wall_between(grid, x, y, nx, ny)

    def _generate_maze(
        self,
        grid: Grid,
        forbidden: ForbiddenSet | None = None,
    ) -> Grid:
        """
        Generate a maze directly inside an existing grid.
        """
        self._validate_grid(grid)

        rng = random.Random(
            None if self.seed is None else f"signed:{self.seed}"
        )
        start = self._pick_start_cell(grid, forbidden)

        self._dfs_generate(grid, rng, start, forbidden)

        if not self.perfect:
            self._add_extra_openings(grid, rng, forbidden)

        self._reset_visited(grid)
        return grid

    # ------------------------------------------------------------------
    # Solver (BFS)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_points(grid: Grid, entry: Coord, exit_: Coord) -> None:
        """Validate entry and exit coordinates."""
        if not grid or not grid[0]:
            raise ValueError("Maze grid cannot be empty.")

        width = len(grid[0])
        height = len(grid)

        entry_x, entry_y = entry
        exit_x, exit_y = exit_

        if not (0 <= entry_x < width and 0 <= entry_y < height):
            raise ValueError("Entry point is outside the maze bounds.")
        if not (0 <= exit_x < width and 0 <= exit_y < height):
            raise ValueError("Exit point is outside the maze bounds.")
        if entry == exit_:
            raise ValueError("Entry and exit must be different.")

    @staticmethod
    def _reconstruct_path(
        parents: ParentMap,
        entry: Coord,
        exit_: Coord,
    ) -> str:
        """
        Reconstruct the shortest path from entry to exit.

        Returns a string made of N, E, S, W direction characters.
        """
        moves: list[str] = []
        current = exit_

        while current != entry:
            parent_info = parents.get(current)

            if parent_info is None:
                raise ValueError("No valid path found from entry to exit.")

            previous, direction = parent_info
            moves.append(direction)
            current = previous

        moves.reverse()
        return "".join(moves)

    @staticmethod
    def _solve_maze(grid: Grid, entry: Coord, exit_: Coord) -> str:
        """
        Solve the maze using BFS and return the shortest path.
        """
        MazeGenerator._validate_points(grid, entry, exit_)

        queue: deque[Coord] = deque([entry])
        visited: set[Coord] = {entry}
        parents: ParentMap = {entry: None}

        while queue:
            x, y = queue.popleft()

            if (x, y) == exit_:
                return MazeGenerator._reconstruct_path(parents, entry, exit_)

            for nx, ny, direction in MazeGenerator._get_open_neighbors(
                x,
                y,
                grid,
            ):
                neighbor = (nx, ny)
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                parents[neighbor] = ((x, y), direction)
                queue.append(neighbor)

        raise ValueError("No valid path found from entry to exit.")

    # ------------------------------------------------------------------
    # Encoder
    # ------------------------------------------------------------------

    @staticmethod
    def _cell_to_hex(cell: "MazeGenerator.Cell") -> str:
        """
        Convert one cell to its hexadecimal wall encoding.
        """
        value = 0
        if cell.north:
            value |= 1
        if cell.east:
            value |= 2
        if cell.south:
            value |= 4
        if cell.west:
            value |= 8
        return format(value, "X")

    @staticmethod
    def _encode_grid(grid: Grid) -> list[str]:
        """Encode the whole maze grid into hexadecimal rows."""
        if not grid or not grid[0]:
            raise ValueError("Maze grid cannot be empty.")
        return [
            "".join(MazeGenerator._cell_to_hex(cell) for cell in row)
            for row in grid
        ]

    @staticmethod
    def _format_output(
        grid: Grid,
        entry: Coord,
        exit_: Coord,
        path: str,
    ) -> str:
        """Build the full output text for the maze file."""
        rows = MazeGenerator._encode_grid(grid)
        return (
            "\n".join(rows)
            + "\n\n"
            + f"{entry[0]},{entry[1]}\n"
            + f"{exit_[0]},{exit_[1]}\n"
            + f"{path}\n"
        )


# Module-level alias for backward compatibility
_pattern_coords = MazeGenerator._pattern_coords
