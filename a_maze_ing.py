import sys
from typing import Any
# any for flexibale input
from maze.encoder import write_output
from maze.generator import generate_maze
from maze.grid import create_grid
from maze.pattern import stamp_42_pattern
from maze.solver import solve_maze
from parsing.config_parser import parse_config


def _validate_args(argv: list[str]) -> str:
    """Validate command-line arguments and return config file path."""
    if len(argv) != 2:
        raise ValueError("Usage: python3 a_maze_ing.py config.txt")
    return argv[1]


def _get_attr(config: Any, name: str) -> Any:
    """Return a required config attribute."""
    if not hasattr(config, name):
        raise ValueError(f"Missing required config field: {name}")
    return getattr(config, name)


def _validate_coord(value: Any, field_name: str) -> tuple[int, int]:
    """Validate a coordinate pair."""
    if not isinstance(value, tuple) or len(value) != 2:
        raise ValueError(f"{field_name} must be a tuple of two integers.")

    x, y = value
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError(f"{field_name} must contain integers only.")

    return (x, y)


def _validate_config(config: Any) -> tuple[
    int,
    int,
    tuple[int, int],
    tuple[int, int],
    str,
    bool,
    int | None,
]:
    """Extract and validate config fields."""
    width = _get_attr(config, "width")
    height = _get_attr(config, "height")
    entry = _get_attr(config, "entry")
    exit_ = _get_attr(config, "exit")
    output_file = _get_attr(config, "output_file")
    perfect = _get_attr(config, "perfect")
    seed = getattr(config, "seed", None)

    if not isinstance(width, int) or width <= 0:
        raise ValueError("WIDTH must be a positive integer.")

    if not isinstance(height, int) or height <= 0:
        raise ValueError("HEIGHT must be a positive integer.")

    entry = _validate_coord(entry, "ENTRY")
    exit_ = _validate_coord(exit_, "EXIT")

    if not isinstance(output_file, str) or not output_file.strip():
        raise ValueError("OUTPUT_FILE must be a non-empty string.")

    if not isinstance(perfect, bool):
        raise ValueError("PERFECT must be a boolean.")

    if seed is not None and not isinstance(seed, int):
        raise ValueError("SEED must be an integer or None.")

    entry_x, entry_y = entry
    exit_x, exit_y = exit_

    if not (0 <= entry_x < width and 0 <= entry_y < height):
        raise ValueError("ENTRY is outside maze bounds.")

    if not (0 <= exit_x < width and 0 <= exit_y < height):
        raise ValueError("EXIT is outside maze bounds.")

    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different.")

    return (width, height, entry, exit_, output_file, perfect, seed)


def _validate_not_in_pattern(
    entry: tuple[int, int],
    exit_: tuple[int, int],
    forbidden: set[tuple[int, int]],
) -> None:
    """Ensure entry and exit are not inside the 42 pattern."""
    if entry in forbidden:
        raise ValueError("ENTRY cannot be inside the 42 pattern.")

    if exit_ in forbidden:
        raise ValueError("EXIT cannot be inside the 42 pattern.")


def main() -> int:
    """Run the maze generation pipeline."""
    try:
        config_file = _validate_args(sys.argv)
        config = parse_config(config_file)

        width, height, entry, exit_, output_file, perfect, seed = (
            _validate_config(config)
        )

        grid = create_grid(width, height)
        forbidden = stamp_42_pattern(grid)

        _validate_not_in_pattern(entry, exit_, forbidden)

        generate_maze(
            grid=grid,
            seed=seed,
            perfect=perfect,
            forbidden=forbidden,
        )

        path = solve_maze(grid, entry, exit_)

        write_output(
            output_file=output_file,
            grid=grid,
            entry=entry,
            exit_=exit_,
            path=path,
        )

        return 0

    except FileNotFoundError as error:
        print(f"Error: {error}")
        return 1
    except ValueError as error:
        print(f"Error: {error}")
        return 1
    except OSError as error:
        print(f"Error: {error}")
        return 1
    except Exception as error:
        print(f"Unexpected error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
