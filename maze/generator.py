import random
from typing import TypeAlias

from .grid import Coord, Grid, get_unvisited_neighbors, remove_wall_between

ForbiddenSet: TypeAlias = set[Coord]


def _validate_grid(grid: Grid) -> None:
    """Validate that the maze grid is not empty."""
    if not grid or not grid[0]:
        raise ValueError("Maze grid cannot be empty.")


def _pick_start_cell(
    grid: Grid,
    forbidden: ForbiddenSet | None = None,
) -> Coord:
    """
    Return a valid starting cell for DFS generation.

    The first available non-forbidden cell is selected.
    Raise ValueError if no valid starting cell exists.
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


def _reset_visited(grid: Grid) -> None:
    """Clear the visited flag on every cell after generation."""
    for row in grid:
        for cell in row:
            cell.visited = False


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
        neighbors = get_unvisited_neighbors(x, y, grid, forbidden)

        if not neighbors:
            stack.pop()
            continue

        nx, ny, _ = rng.choice(neighbors)
        remove_wall_between(grid, x, y, nx, ny)
        grid[ny][nx].visited = True
        stack.append((nx, ny))


def _add_extra_openings(
    grid: Grid,
    rng: random.Random,
    forbidden: ForbiddenSet | None = None,
) -> None:
    """
    Add extra openings to create loops in a non-perfect maze.

    Only opens internal walls between non-forbidden adjacent cells.
    Uses a low probability to avoid making the maze too open.
    """
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
                remove_wall_between(grid, x, y, nx, ny)


def generate_maze(
    grid: Grid,
    seed: int | None = None,
    perfect: bool = True,
    forbidden: ForbiddenSet | None = None,
) -> Grid:
    """
    Generate a maze directly inside an existing grid.

    Args:
        grid: Maze grid already created.
        seed: Optional random seed for reproducibility.
        perfect: Whether the maze must be perfect.
        forbidden: Cells that must remain blocked, such as the 42 pattern.

    Returns:
        The same grid, modified in place and also returned for convenience.

    Raises:
        ValueError: If the grid is empty or no valid start exists.
    """
    _validate_grid(grid)

    rng = random.Random(seed)
    start = _pick_start_cell(grid, forbidden)

    _dfs_generate(grid, rng, start, forbidden)

    if not perfect:
        _add_extra_openings(grid, rng, forbidden)

    _reset_visited(grid)
    return grid
