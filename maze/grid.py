from typing import TypeAlias

from .cell import Cell

Grid: TypeAlias = list[list[Cell]]
Neighbor: TypeAlias = tuple[int, int, str]
Coord: TypeAlias = tuple[int, int]


def create_grid(width: int, height: int) -> Grid:
    """Create a 2D grid of cells with all walls initially closed."""
    return [[Cell() for _ in range(width)] for _ in range(height)]


def in_bounds(x: int, y: int, width: int, height: int) -> bool:
    """Return True if the coordinates are inside the grid."""
    return 0 <= x < width and 0 <= y < height


def get_neighbors(
    x: int,
    y: int,
    width: int,
    height: int,
) -> list[Neighbor]:
    """
    Return all valid neighbors of a cell.

    Each neighbor is represented as:
    (nx, ny, direction_from_current)
    """
    neighbors: list[Neighbor] = []

    if in_bounds(x, y - 1, width, height):
        neighbors.append((x, y - 1, "N"))
    if in_bounds(x + 1, y, width, height):
        neighbors.append((x + 1, y, "E"))
    if in_bounds(x, y + 1, width, height):
        neighbors.append((x, y + 1, "S"))
    if in_bounds(x - 1, y, width, height):
        neighbors.append((x - 1, y, "W"))
    return neighbors


def get_unvisited_neighbors(
    x: int,
    y: int,
    grid: Grid,
    forbidden: set[Coord] | None = None,
) -> list[Neighbor]:
    """Return neighbors that have not been visited and are not forbidden."""
    height = len(grid)
    width = len(grid[0])
    neighbors = get_neighbors(x, y, width, height)

    return [
        (nx, ny, direction)
        for nx, ny, direction in neighbors
        if not grid[ny][nx].visited
        and (forbidden is None or (nx, ny) not in forbidden)
    ]


def remove_wall_between(
    grid: Grid,
    x: int,
    y: int,
    nx: int,
    ny: int,
) -> None:
    """
    Remove the wall between two adjacent cells.

    Both cells are updated so wall data stays coherent.
    Raise ValueError if the cells are not adjacent.
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


def is_open(grid: Grid, x: int, y: int, direction: str) -> bool:
    """
    Return True if movement from (x, y) in the given direction is possible.

    Valid directions are: N, E, S, W.
    """
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


def get_open_neighbors(x: int, y: int, grid: Grid) -> list[Neighbor]:
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
