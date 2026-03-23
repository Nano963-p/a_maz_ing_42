from typing import TypeAlias

from .grid import Grid

Coord: TypeAlias = tuple[int, int]

PATTERN_42: list[str] = [
    "4  2 2",
    "4  2 2",
    "444222",
    "  4  2",
    "  4222",
]

_PATTERN_HEIGHT: int = len(PATTERN_42)
_PATTERN_WIDTH: int = max(len(row) for row in PATTERN_42)

PATTERN_42 = [row.ljust(_PATTERN_WIDTH) for row in PATTERN_42]

MIN_WIDTH: int = _PATTERN_WIDTH + 2
MIN_HEIGHT: int = _PATTERN_HEIGHT + 2


def can_draw_42(width: int, height: int) -> bool:
    """Return True if the maze is large enough to fit the 42 pattern."""
    return width >= MIN_WIDTH and height >= MIN_HEIGHT


def _close_cell(grid: Grid, x: int, y: int) -> None:
    """Set all four walls of a cell to closed."""
    cell = grid[y][x]
    cell.north = True
    cell.east = True
    cell.south = True
    cell.west = True


def _pattern_coords(width: int, height: int) -> list[Coord]:
    """
    Compute centered coordinates for the 42 pattern inside the maze.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        List of (x, y) coordinates to stamp as fully closed cells.
    """
    offset_x = (width - _PATTERN_WIDTH) // 2
    offset_y = (height - _PATTERN_HEIGHT) // 2

    return [
        (offset_x + px, offset_y + py)
        for py, row in enumerate(PATTERN_42)
        for px, ch in enumerate(row)
        if ch != " "
    ]


def stamp_42_pattern(grid: Grid) -> set[Coord]:
    """
    Stamp the 42 pattern into the grid before maze generation.

    These cells must then be passed to the generator as forbidden cells
    so DFS never enters them.

    Args:
        grid: The maze grid.

    Returns:
        A set of forbidden coordinates corresponding to the 42 pattern.

    Raises:
        ValueError: If the grid is empty.
    """
    if not grid or not grid[0]:
        raise ValueError("Maze grid cannot be empty.")

    height = len(grid)
    width = len(grid[0])

    if not can_draw_42(width, height):
        print("Error: Maze too small to include the 42 pattern.")
        return set()

    coords = _pattern_coords(width, height)

    for x, y in coords:
        _close_cell(grid, x, y)

    return set(coords)
