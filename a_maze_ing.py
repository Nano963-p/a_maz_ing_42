import os
import sys
import time
from typing import Protocol, TypeAlias

from ascii_render import (
    hide_cursor,
    init_screen,
    maze_to_string,
    next_theme,
    refresh_screen,
    render_animated,
    render_maze,
    show_cursor,
)
from config_parser import parse_config
from intro_animation import intro_screen
from mazegen.mazegenerator import Coord, Grid, MazeGenerator


class ConfigLike(Protocol):
    """Typed shape of the parsed config object used by this module.

    Defines the interface expected from the configuration dataclass,
    allowing type-safe access to all maze parameters without coupling
    to the concrete Config class from config_parser.
    """

    width: int
    height: int
    seed: str | None
    perfect: bool
    entry: Coord
    exit: Coord
    output_file: str
    theme: str
    animate: bool
    draw_pattern: bool


BuildMazeResult: TypeAlias = tuple[Grid, Coord, Coord, str, set[Coord]]


def clear() -> None:
    """Clear the terminal screen."""
    os.system("clear")


def _print_menu(theme_name: str) -> None:
    """Print the interactive main menu to stdout.

    Args:
        theme_name: The name of the currently active visual theme,
                    displayed at the bottom of the menu.
    """
    print("\n" + "=" * 36)
    print("           A-Maze-ing")
    print("=" * 36)
    print(" 1. Re-generate a new maze")
    print(" 2. Show / Hide solution path")
    print(" 3. Move player to the goal")
    print(" 4. Change theme")
    print(" 5. Quit")
    print(f" Theme: {theme_name}")
    print("=" * 36)


def _build_maze(
    config: ConfigLike,
    show_path: bool,
    animate: bool,
    theme_name: str,
) -> BuildMazeResult:
    """Generate a new maze and render it to the terminal.

    Creates a MazeGenerator from the given config, generates the maze,
    writes the result to the configured output file, then either renders
    it statically or with an animated reveal depending on the animate flag.

    Args:
        config:     Parsed configuration object with maze parameters.
        show_path:  Whether to overlay the solution path on the static render.
        animate:    If True, reveal the maze line-by-line with a delay;
                    if False, print it all at once.
        theme_name: Name of the visual theme to use for rendering.

    Returns:
        A tuple of (grid, entry, exit_, path, forbidden) where:
          - grid      is the 2-D cell array,
          - entry     is the start coordinate,
          - exit_     is the goal coordinate,
          - path      is the BFS solution as a direction string,
          - forbidden is the set of pattern-stamped (impassable) cells.
    """
    entry: Coord = config.entry
    exit_: Coord = config.exit

    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        seed=config.seed,
        perfect=config.perfect,
        entry=entry,
        exit_=exit_,
        draw_pattern=config.draw_pattern,
    )
    grid, path, forbidden = generator.generate()
    generator.validate_no_3x3(grid)
    generator.write_output(config.output_file, grid, path)

    if animate:
        render_animated(
            grid,
            entry,
            exit_,
            forbidden=forbidden,
            theme_name=theme_name,
        )
    else:
        render_maze(
            grid,
            entry,
            exit_,
            path=path,
            show_path=show_path,
            forbidden=forbidden,
            theme_name=theme_name,
        )

    return grid, entry, exit_, path, forbidden


def move_coord(pos: Coord, step: str) -> Coord:
    """Return the new coordinate after taking one step in the given direction.

    Args:
        pos:  Current (x, y) position.
        step: Direction character — one of 'N', 'S', 'E', 'W'.

    Returns:
        The updated (x, y) coordinate. Returns pos unchanged if step
        is not a recognised direction character.
    """
    x, y = pos
    if step == "N":
        return (x, y - 1)
    if step == "S":
        return (x, y + 1)
    if step == "E":
        return (x + 1, y)
    if step == "W":
        return (x - 1, y)
    return pos


def animate_player(
    grid: Grid,
    entry: Coord,
    exit_: Coord,
    path: str,
    forbidden: set[Coord],
    theme_name: str,
) -> None:
    """Animate a player token moving along the solution path in the terminal.

    Hides the cursor, initialises a full-screen buffer, then redraws the
    maze on each step with the player's current position highlighted.
    A 'visited' trail is accumulated so already-walked cells are marked.
    Restores the cursor in a finally block to avoid leaving the terminal
    in a broken state if interrupted.

    Args:
        grid:       The solved maze grid.
        entry:      Starting coordinate of the player.
        exit_:      Target coordinate the player is heading to.
        path:       Solution path as a string of direction characters.
        forbidden:  Set of impassable pattern cells.
        theme_name: Visual theme used for rendering.
    """
    player_pos = entry
    visited: set[Coord] = set()
    hide_cursor()
    init_screen()
    try:
        sys.stdout.write(
            maze_to_string(
                grid,
                entry,
                exit_,
                forbidden=forbidden,
                theme_name=theme_name,
                player_pos=player_pos,
                visited=visited,
                show_intro=False,
            )
        )
        sys.stdout.flush()
        time.sleep(0.2)

        for step in path:
            visited.add(player_pos)
            player_pos = move_coord(player_pos, step)
            refresh_screen()
            sys.stdout.write(
                maze_to_string(
                    grid,
                    entry,
                    exit_,
                    forbidden=forbidden,
                    theme_name=theme_name,
                    player_pos=player_pos,
                    visited=visited,
                    show_intro=False,
                )
            )
            sys.stdout.flush()
            time.sleep(0.12)

        sys.stdout.write("\n\n🎉 Goal reached! 🎉\n")
        sys.stdout.flush()
        time.sleep(0.8)
    finally:
        show_cursor()


def main() -> int:
    """Entry point for the A-Maze-ing interactive loop.

    Parses the config file given as a command-line argument, generates
    the initial maze, then enters a menu-driven loop letting the user
    re-generate, toggle the solution path, animate the player, switch
    themes, or quit.

    Returns:
        0 on clean exit, 1 if arguments are missing or config parsing fails.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1

    parsed = parse_config(sys.argv[1])
    if parsed is None:
        return 1

    config: ConfigLike = parsed
    show_path = False
    theme_name = config.theme

    grid, entry, exit_, path, forbidden = _build_maze(
        config,
        show_path,
        animate=config.animate,
        theme_name=theme_name,
    )

    while True:
        _print_menu(theme_name)
        choice = input("Choice (1-5): ").strip()
        if choice == "1":
            clear()
            if config.seed is not None:
                print(
                    f"Re-generation is disabled: a seed ({config.seed}) is "
                    "set in your config.\n"
                    "Remove or unset SEED in config.txt to generate new mazes."
                )
                render_maze(
                    grid,
                    entry,
                    exit_,
                    path,
                    show_path,
                    forbidden,
                    theme_name,
                )
            else:
                grid, entry, exit_, path, forbidden = _build_maze(
                    config,
                    show_path,
                    animate=False,
                    theme_name=theme_name,
                )
        elif choice == "2":
            clear()
            show_path = not show_path
            print(f"Path display: {'ON' if show_path else 'OFF'}")
            render_maze(
                grid,
                entry,
                exit_,
                path,
                show_path,
                forbidden,
                theme_name,
            )
        elif choice == "3":
            clear()
            animate_player(grid, entry, exit_, path, forbidden, theme_name)
            clear()
            render_maze(
                grid,
                entry,
                exit_,
                path,
                show_path,
                forbidden,
                theme_name,
            )
        elif choice == "4":
            clear()
            theme_name = next_theme(theme_name)
            print(f"Theme changed to: {theme_name}")
            render_maze(
                grid,
                entry,
                exit_,
                path,
                show_path,
                forbidden,
                theme_name,
            )
        elif choice == "5":
            clear()
            print("Goodbye!")
            break
        else:
            clear()
            render_maze(
                grid,
                entry,
                exit_,
                path,
                show_path,
                forbidden,
                theme_name,
            )

    return 0


if __name__ == "__main__":
    try:
        intro_screen()
        raise SystemExit(main())
    except (Exception, KeyboardInterrupt) as err:
        print(f"{err}", file=sys.stderr)
