import sys
import time
from mazegen.mazegenerator import Grid, Coord

RESET = "\033[0m"
BOLD = "\033[1m"

WHITE = "\033[97m"
YELLOW = "\033[93m"
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"

COLORS = {
    "1": (YELLOW, "Yellow"),
    "2": (RED, "Red"),
    "3": (GREEN, "Green"),
    "4": (CYAN, "Cyan"),
    "5": (MAGENTA, "Magenta"),
}

THEMES: dict[str, dict[str, object]] = {
    "dungeon": {
        "wall_color": WHITE,
        "path_color": YELLOW,
        "forbidden_color": RED,
        "entry_symbol": "☻",
        "exit_symbol": "☠",
        "path_symbol": "·",
        "empty_symbol": " ",
        "forbidden_symbol": "█",
        "intro": "Entering the dungeon...",
        "chars": {
            "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
            "h": "─", "v": "│", "tm": "┬", "bm": "┴",
            "lm": "├", "rm": "┤", "cross": "┼",
        },
    },
    "ice": {
        "wall_color": CYAN,
        "path_color": WHITE,
        "forbidden_color": BLUE,
        "entry_symbol": "❄",
        "exit_symbol": "☃",
        "path_symbol": "•",
        "empty_symbol": " ",
        "forbidden_symbol": "░",
        "intro": "A frozen maze appears...",
        "chars": {
            "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
            "h": "═", "v": "║", "tm": "╦", "bm": "╩",
            "lm": "╠", "rm": "╣", "cross": "╬",
        },
    },
    "neon": {
        "wall_color": MAGENTA,
        "path_color": CYAN,
        "forbidden_color": YELLOW,
        "entry_symbol": "☻",
        "exit_symbol": "☢",
        "path_symbol": "•",
        "empty_symbol": " ",
        "forbidden_symbol": "▓",
        "intro": "Booting neon labyrinth...",
        "chars": {
            "tl": "┏", "tr": "┓", "bl": "┗", "br": "┛",
            "h": "━", "v": "┃", "tm": "┳", "bm": "┻",
            "lm": "┣", "rm": "┫", "cross": "╋",
        },
    },
    "forest": {
        "wall_color": GREEN,
        "path_color": YELLOW,
        "forbidden_color": MAGENTA,
        "entry_symbol": "♞",
        "exit_symbol": "🏕",
        "path_symbol": "·",
        "empty_symbol": " ",
        "forbidden_symbol": "█",
        "intro": "Entering the forest maze...",
        "chars": {
            "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
            "h": "─", "v": "│", "tm": "┬", "bm": "┴",
            "lm": "├", "rm": "┤", "cross": "┼",
        },
    },
}

THEME_ORDER = ["dungeon", "ice", "neon", "forest"]


def get_theme(name: str) -> dict[str, object]:
    """Return the theme dict for the given name, defaulting to 'dungeon'.

    Args:
        name: Theme name to look up.

    Returns:
        The matching theme dict, or the 'dungeon' theme if name is unknown.
    """
    return THEMES.get(name, THEMES["dungeon"])


def next_theme(current: str) -> str:
    """Return the name of the next theme in the rotation order.

    Cycles through THEME_ORDER.  If current is not found, returns the
    first theme.

    Args:
        current: Name of the currently active theme.

    Returns:
        Name of the next theme.
    """
    if current not in THEME_ORDER:
        return THEME_ORDER[0]
    index = THEME_ORDER.index(current)
    return THEME_ORDER[(index + 1) % len(THEME_ORDER)]


def _build_path_cells(entry: Coord, path: str) -> set[Coord]:
    """Compute the set of all coordinates visited by the solution path.

    Starts from entry and follows each direction character in path,
    collecting every coordinate including the starting cell.

    Args:
        entry: Starting (x, y) coordinate.
        path:  Direction string made of 'N', 'S', 'E', 'W' characters.

    Returns:
        Set of (x, y) coordinates that lie on the solution path.
    """
    cells: set[Coord] = set()
    x, y = entry
    cells.add((x, y))
    for move in path:
        if move == "N":
            y -= 1
        elif move == "S":
            y += 1
        elif move == "E":
            x += 1
        elif move == "W":
            x -= 1
        cells.add((x, y))
    return cells


def _symbol_text(symbol: str) -> str:
    """Wrap a symbol in single spaces so it fills a 3-character cell slot.

    Args:
        symbol: A single display character or emoji.

    Returns:
        The symbol padded to ' symbol ' (3 chars wide).
    """
    return f" {symbol} "


def _wall_color(theme_name: str) -> str:
    """Return the ANSI wall-color escape code for the given theme.

    Args:
        theme_name: Name of the active theme.

    Returns:
        ANSI escape string for the theme's wall color.
    """
    theme = get_theme(theme_name)
    return str(theme["wall_color"])


def _cell_content(
    x: int,
    y: int,
    entry: Coord,
    exit_: Coord,
    path_cells: set[Coord],
    forbidden: set[Coord],
    theme_name: str,
    player_pos: Coord | None = None,
    visited: set[Coord] | None = None,
) -> str:
    """Return the coloured 3-character string to render inside one cell.

    Priority order (highest first):
      1. Player position  → green star symbol
      2. Entry cell       → themed entry symbol
      3. Exit cell        → themed exit symbol
      4. Forbidden cell   → themed forbidden symbol (repeated 3×)
      5. Visited cell     → themed path symbol (player trail)
      6. Path cell        → themed path symbol (solution overlay)
      7. Empty cell       → three spaces

    Args:
        x, y:        Grid coordinates of the cell being rendered.
        entry:       Maze entry coordinate.
        exit_:       Maze exit coordinate.
        path_cells:  Set of coordinates on the solution path.
        forbidden:   Set of impassable pattern cells.
        theme_name:  Active visual theme.
        player_pos:  Current player position, or None if not animating.
        visited:     Cells already walked by the player, or None.

    Returns:
        A coloured 3-character wide string for the cell interior.
    """
    theme = get_theme(theme_name)
    if visited is None:
        visited = set()
    if player_pos is not None and (x, y) == player_pos:
        return GREEN + BOLD + " ✦ " + RESET
    if (x, y) == entry:
        return GREEN + BOLD + _symbol_text(str(theme["entry_symbol"])) + RESET
    if (x, y) == exit_:
        return RED + BOLD + _symbol_text(str(theme["exit_symbol"])) + RESET
    if (x, y) in forbidden:
        return (
            str(theme["forbidden_color"])
            + BOLD
            + (str(theme["forbidden_symbol"]) * 3)
            + RESET
        )
    if (x, y) in visited:
        return (
            str(theme["path_color"])
            + BOLD
            + _symbol_text(str(theme["path_symbol"]))
            + RESET
        )
    if (x, y) in path_cells:
        return (
            str(theme["path_color"])
            + BOLD
            + _symbol_text(str(theme["path_symbol"]))
            + RESET
        )
    return str(theme["empty_symbol"]) * 3


def _render_lines(
    grid: Grid,
    entry: Coord,
    exit_: Coord,
    path_cells: set[Coord],
    wall_color: str,
    forbidden: set[Coord],
    theme_name: str,
    player_pos: Coord | None = None,
    visited: set[Coord] | None = None,
    show_intro: bool = True,
) -> list[str]:
    """Build the complete list of terminal lines that represent the maze.

    Iterates over each row, generating a top-border line followed by a
    middle (cell content + vertical walls) line.  Appends a single bottom
    border at the end.  Uses box-drawing characters from the active theme.

    Args:
        grid:        2-D list of Cell objects.
        entry:       Maze entry coordinate.
        exit_:       Maze exit coordinate.
        path_cells:  Coordinates to highlight as part of the solution.
        wall_color:  ANSI escape code for wall drawing characters.
        forbidden:   Set of impassable pattern cells.
        theme_name:  Active visual theme.
        player_pos:  Current player position for animation, or None.
        visited:     Player trail cells for animation, or None.
        show_intro:  If True, prepend the theme's intro message line.

    Returns:
        List of strings, one per terminal line, ready to be joined and
        printed.
    """
    height = len(grid)
    width = len(grid[0])
    theme = get_theme(theme_name)
    chars = theme["chars"]
    assert isinstance(chars, dict)
    h_char = str(chars["h"])
    v_char = str(chars["v"])
    lines: list[str] = []
    if show_intro:
        lines.append(str(theme["intro"]))

    for y in range(height):
        top = ""
        for x in range(width):
            if x == 0:
                top += wall_color + BOLD + str(chars["tl"] if y == 0 else
                                               chars["lm"]) + RESET
            if grid[y][x].north:
                top += wall_color + BOLD + (h_char * 3) + RESET
            else:
                top += "   "
            if x == width - 1:
                top += wall_color + BOLD + str(chars["tr"] if y == 0 else
                                               chars["rm"]) + RESET
            else:
                top += wall_color + BOLD + str(chars["tm"] if y == 0 else
                                               chars["cross"]) + RESET
        lines.append(top)

        middle = ""
        for x in range(width):
            if x == 0:
                if grid[y][x].west:
                    middle += wall_color + BOLD + v_char + RESET
                else:
                    middle += " "
            middle += _cell_content(
                x, y, entry, exit_, path_cells, forbidden, theme_name,
                player_pos, visited
            )
            if grid[y][x].east:
                middle += wall_color + BOLD + v_char + RESET
            else:
                middle += " "
        lines.append(middle)

    bottom = ""
    for x in range(width):
        if x == 0:
            bottom += wall_color + BOLD + str(chars["bl"]) + RESET
        bottom += wall_color + BOLD + (h_char * 3) + RESET
        if x == width - 1:
            bottom += wall_color + BOLD + str(chars["br"]) + RESET
        else:
            bottom += wall_color + BOLD + str(chars["bm"]) + RESET
    lines.append(bottom)
    return lines


def render_maze(
    grid: Grid,
    entry: Coord,
    exit_: Coord,
    path: str | None = None,
    show_path: bool = False,
    forbidden: set[Coord] | None = None,
    theme_name: str = "dungeon",
    player_pos: Coord | None = None,
    visited: set[Coord] | None = None,
    show_intro: bool = True,
) -> None:
    """Print the maze to stdout in a single call.

    Builds the path-cell set when show_path is True, then delegates to
    _render_lines() and joins the result with newlines.

    Args:
        grid:       2-D Cell grid to render.
        entry:      Maze entry coordinate.
        exit_:      Maze exit coordinate.
        path:       Solution direction string, used when show_path is True.
        show_path:  Whether to overlay solution path markers.
        forbidden:  Impassable pattern cells (defaults to empty set).
        theme_name: Visual theme (defaults to 'dungeon').
        player_pos: Player position for animation overlays, or None.
        visited:    Player trail cells for animation, or None.
        show_intro: If True, print the theme intro line above the maze.
    """
    if not grid or not grid[0]:
        print("Error: empty grid.")
        return
    path_cells: set[Coord] = set()
    if show_path and path:
        path_cells = _build_path_cells(entry, path)
    chosen_wall_color = _wall_color(theme_name)
    lines = _render_lines(
        grid,
        entry,
        exit_,
        path_cells,
        chosen_wall_color,
        forbidden or set(),
        theme_name,
        player_pos,
        visited,
        show_intro,
    )
    print("\n".join(lines))


def maze_to_string(
    grid: Grid,
    entry: Coord,
    exit_: Coord,
    path: str | None = None,
    show_path: bool = False,
    forbidden: set[Coord] | None = None,
    theme_name: str = "dungeon",
    player_pos: Coord | None = None,
    visited: set[Coord] | None = None,
    show_intro: bool = True,
) -> str:
    """Return the maze as a single string without printing it.

    Identical in parameters to render_maze(), but returns the result
    instead of printing it.  Used by animate_player() to write to stdout
    manually so the cursor position can be controlled.

    Args:
        grid:       2-D Cell grid to render.
        entry:      Maze entry coordinate.
        exit_:      Maze exit coordinate.
        path:       Solution direction string, used when show_path is True.
        show_path:  Whether to overlay solution path markers.
        forbidden:  Impassable pattern cells (defaults to empty set).
        theme_name: Visual theme (defaults to 'dungeon').
        player_pos: Player position for animation overlays, or None.
        visited:    Player trail cells for animation, or None.
        show_intro: If True, include the theme intro line at the top.

    Returns:
        The full maze representation as a newline-joined string.
    """
    path_cells: set[Coord] = set()
    if show_path and path:
        path_cells = _build_path_cells(entry, path)
    chosen_wall_color = _wall_color(theme_name)
    lines = _render_lines(
        grid,
        entry,
        exit_,
        path_cells,
        chosen_wall_color,
        forbidden or set(),
        theme_name,
        player_pos,
        visited,
        show_intro,
    )
    return "\n".join(lines)


def render_animated(
    grid: Grid,
    entry: Coord,
    exit_: Coord,
    forbidden: set[Coord] | None = None,
    delay: float = 0.05,
    theme_name: str = "dungeon",
) -> None:
    """Reveal the maze line by line with a short delay between each line.

    Used at startup when ANIMATE=true in config.txt.  Prints each line of
    the maze individually with a sleep between them for a scrolling effect.

    Args:
        grid:       2-D Cell grid to render.
        entry:      Maze entry coordinate.
        exit_:      Maze exit coordinate.
        forbidden:  Impassable pattern cells (defaults to empty set).
        delay:      Seconds to wait between printing each line.
        theme_name: Visual theme (defaults to 'dungeon').
    """
    lines = _render_lines(
        grid,
        entry,
        exit_,
        set(),
        _wall_color(theme_name),
        forbidden or set(),
        theme_name,
    )
    for line in lines:
        print(line)
        time.sleep(delay)


def init_screen() -> None:
    """Clear the terminal and move the cursor to the top-left corner.

    Writes the ANSI escape sequence ESC[2J (erase display) followed by
    ESC[H (cursor home).  Used before starting an animation loop.
    """
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def refresh_screen() -> None:
    """Move the cursor back to the top-left corner without clearing.

    Writes ESC[H so the next render overwrites the previous frame in place,
    creating a smooth animation effect without flicker.
    """
    sys.stdout.write("\033[H")
    sys.stdout.flush()


def hide_cursor() -> None:
    """Hide the terminal cursor using the ANSI escape sequence ESC[?25l."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    """Restore the terminal cursor using the ANSI escape sequence ESC[?25h."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
