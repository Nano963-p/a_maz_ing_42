import sys
import time
from maze.ascii_render import (
    render_maze,
    render_animated,
    maze_to_string,
    next_theme,
    init_screen,
    refresh_screen,
    hide_cursor,
    show_cursor,
)
from maze.generator import generate_maze
from maze.grid import Grid, Coord, create_grid
from maze.pattern import stamp_42_pattern
from maze.solver import solve_maze
from maze.encoder import write_output
from parsing.config_parser import parse_config
from maze.intro_animation import intro_screen

intro_screen()


def _print_menu(theme_name: str) -> None:
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


def _build_maze(config: object, show_path: bool, animate: bool,
                theme_name: str):
    entry: Coord = config.entry
    exit_: Coord = config.exit
    grid: Grid = create_grid(config.width, config.height)
    forbidden = stamp_42_pattern(grid)

    generate_maze(grid=grid, seed=config.seed, perfect=config.perfect,
                  forbidden=forbidden)
    path = solve_maze(grid, entry, exit_)
    write_output(config.output_file, grid, entry, exit_, path)

    if animate:
        render_animated(grid, entry, exit_, forbidden=forbidden,
                        theme_name=theme_name)
    else:
        render_maze(grid, entry, exit_, path=path, show_path=show_path,
                    forbidden=forbidden, theme_name=theme_name)

    return grid, entry, exit_, path, forbidden


def move_coord(pos: Coord, step: str) -> Coord:
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
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1

    config = parse_config(sys.argv[1])
    if config is None:
        return 1

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
            config.seed = None
            grid, entry, exit_, path, forbidden = _build_maze(
                config,
                show_path,
                animate=False,
                theme_name=theme_name,
            )
        elif choice == "2":
            show_path = not show_path
            print(f"Path display: {'ON' if show_path else 'OFF'}")
            render_maze(grid, entry, exit_, path=path, show_path=show_path,
                        forbidden=forbidden, theme_name=theme_name)
        elif choice == "3":
            animate_player(grid, entry, exit_, path, forbidden, theme_name)
            render_maze(grid, entry, exit_, path=path, show_path=show_path,
                        forbidden=forbidden, theme_name=theme_name)
        elif choice == "4":
            theme_name = next_theme(theme_name)
            print(f"Theme changed to: {theme_name}")
            render_maze(grid, entry, exit_, path=path, show_path=show_path,
                        forbidden=forbidden, theme_name=theme_name)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
