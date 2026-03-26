import sys
import time
from maze.grid import Grid, Coord

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
    return THEMES.get(name, THEMES["dungeon"])


def next_theme(current: str) -> str:
    if current not in THEME_ORDER:
        return THEME_ORDER[0]
    index = THEME_ORDER.index(current)
    return THEME_ORDER[(index + 1) % len(THEME_ORDER)]


def _build_path_cells(entry: Coord, path: str) -> set[Coord]:
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
    return f" {symbol} "


def _wall_color(theme_name: str) -> str:
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
                top += wall_color + BOLD + str(chars["tl"] if y == 0 else chars["lm"]) + RESET
            if grid[y][x].north:
                top += wall_color + BOLD + (h_char * 3) + RESET
            else:
                top += "   "
            if x == width - 1:
                top += wall_color + BOLD + str(chars["tr"] if y == 0 else chars["rm"]) + RESET
            else:
                top += wall_color + BOLD + str(chars["tm"] if y == 0 else chars["cross"]) + RESET
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
    delay: float = 0.03,
    theme_name: str = "dungeon",
) -> None:
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
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def refresh_screen() -> None:
    sys.stdout.write("\033[H")
    sys.stdout.flush()


def hide_cursor() -> None:
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
