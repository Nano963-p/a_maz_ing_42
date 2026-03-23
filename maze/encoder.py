from .cell import Cell
from .grid import Coord, Grid


def cell_to_hex(cell: Cell) -> str:
    """
    Convert one cell to its hexadecimal wall encoding.

    Bit mapping:
        bit 0 -> North
        bit 1 -> East
        bit 2 -> South
        bit 3 -> West

    A closed wall sets the bit to 1.
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


def encode_grid(grid: Grid) -> list[str]:
    """
    Encode the whole maze grid into hexadecimal rows.

    Returns:
        A list of strings, one per maze row.
    """
    if not grid or not grid[0]:
        raise ValueError("Maze grid cannot be empty.")

    return [
        "".join(cell_to_hex(cell) for cell in row)
        for row in grid
    ]


def format_output(
    grid: Grid,
    entry: Coord,
    exit_: Coord,
    path: str,
) -> str:
    """
    Build the full output text for the maze file.

    Format:
        - hex-encoded maze rows
        - empty line
        - entry coordinates
        - exit coordinates
        - shortest path
    """
    rows = encode_grid(grid)

    return (
        "\n".join(rows)
        + "\n\n"
        + f"{entry[0]},{entry[1]}\n"
        + f"{exit_[0]},{exit_[1]}\n"
        + f"{path}\n"
    )


def write_output(
    output_file: str,
    grid: Grid,
    entry: Coord,
    exit_: Coord,
    path: str,
) -> None:
    """
    Write the maze output to a file.

    Args:
        output_file: Destination file path.
        grid: Maze grid.
        entry: Entry coordinates.
        exit_: Exit coordinates.
        path: Shortest path string.
    """
    content = format_output(grid, entry, exit_, path)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(content)
