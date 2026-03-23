from collections import deque
from typing import TypeAlias

from .grid import Coord, Grid, get_open_neighbors

ParentMap: TypeAlias = dict[Coord, tuple[Coord, str] | None]


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


def _reconstruct_path(
    parents: ParentMap,
    entry: Coord,
    exit_: Coord,
) -> str:
    """
    Reconstruct the shortest path from entry to exit.

    The returned path is a string made of N, E, S, W.
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


def solve_maze(grid: Grid, entry: Coord, exit_: Coord) -> str:
    """
    Solve the maze using BFS and return the shortest path.

    Args:
        grid: The maze grid.
        entry: Entry coordinates (x, y).
        exit_: Exit coordinates (x, y).

    Returns:
        The shortest path as a string using N, E, S, W.

    Raises:
        ValueError:
        If the grid or coordinates are invalid, or if no path exists.
    """
    _validate_points(grid, entry, exit_)

    queue: deque[Coord] = deque([entry])
    visited: set[Coord] = {entry}
    parents: ParentMap = {entry: None}

    while queue:
        x, y = queue.popleft()

        if (x, y) == exit_:
            return _reconstruct_path(parents, entry, exit_)

        for nx, ny, direction in get_open_neighbors(x, y, grid):
            neighbor = (nx, ny)

            if neighbor in visited:
                continue

            visited.add(neighbor)
            parents[neighbor] = ((x, y), direction)
            queue.append(neighbor)

    raise ValueError("No valid path found from entry to exit.")
