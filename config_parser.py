import os
import sys
from dataclasses import dataclass
from typing import Optional, TypedDict
from mazegen.mazegenerator import _pattern_coords


@dataclass
class Config:
    """Validated, strongly-typed configuration for a single maze run.

    Instances are produced by ConfigParser.parse() after all values have
    been parsed and validated.  Fields map directly to the keys accepted
    in config.txt.

    Attributes:
        width:        Number of columns in the maze grid.
        height:       Number of rows in the maze grid.
        entry:        (x, y) coordinate of the maze entrance.
        exit:         (x, y) coordinate of the maze exit.
        output_file:  Path where the encoded maze text will be written.
        perfect:      If True, add extra openings to create shortcuts;
                      if False, generate a single-path (harder) maze.
        seed:         Optional RNG seed for reproducible generation.
        animate:      If True, reveal the maze line-by-line on launch.
        theme:        Visual theme name (dungeon / ice / neon / forest).
        draw_pattern: Whether to stamp the 42 pattern into the maze.
                      Set to False automatically when the grid is too small.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[str] = None
    animate: bool = False
    theme: str = "dungeon"
    draw_pattern: bool = True


class _RawConfig(TypedDict):
    """Internal TypedDict holding raw parsed values before validation.

    Values may still be None for optional/boolean keys that failed to parse;
    the validate() step rejects any None that would be illegal.
    """

    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: Optional[bool]
    ANIMATE: Optional[bool]
    SEED: Optional[str]
    THEME: str


_PROJECT_FILES = {
    "ascii_render.py",
    "mazegenerator.py",
    "config_parser.py",
    "intro_animation.py",
    "a_maze_ing.py",
}


class ConfigParser:
    """Parse and validate a maze configuration file.

    The file format is key=value, one entry per line, with '#' comments.
    Supported keys match the fields of Config (case-insensitive).

    Usage::

        parser = ConfigParser("config.txt")
        config = parser.parse()   # returns Config or None on error

    Attributes:
        filepath:      Path to the configuration file.
        config:        Internal raw-value dict populated during parsing.
    """

    _REQUIRED_KEYS = [
        "width", "height", "entry", "exit", "output_file", "perfect"
    ]

    MIN_WIDTH: int = 7
    MIN_HEIGHT: int = 9
    MAX_WIDTH: int = 50
    MAX_HEIGHT: int = 50

    def __init__(self, filepath: str) -> None:
        """Initialise the parser with the path to a config file.

        Args:
            filepath: Path to the config.txt file to be parsed.
        """
        self.filepath = filepath
        self._draw_pattern: bool = True
        self.config: _RawConfig = {
            "WIDTH": 0,
            "HEIGHT": 0,
            "ENTRY": (0, 0),
            "EXIT": (0, 0),
            "OUTPUT_FILE": "output_maze.txt",
            "PERFECT": False,
            "ANIMATE": False,
            "SEED": None,
            "THEME": "dungeon",
        }

    def parse(self) -> Optional[Config]:
        """Read and validate the config file, returning a Config on success.

        Reads the file line by line, strips comments, splits on '=', and
        delegates each key to assign_value().  After all lines are processed,
        checks that every required key was present and calls validate().

        Returns:
            A fully validated Config dataclass, or None if any error
            occurred (file not found, permission denied, missing key,
            invalid value, failed validation).
        """
        keys_seen: set[str] = set()
        try:
            with open(self.filepath, "r") as file:
                for line in file:
                    line = line.split("#")[0].strip()
                    if not line:
                        continue

                    parts = line.split("=", 1)
                    if len(parts) < 2:
                        raise ValueError(
                            f"Invalid line (missing '='): '{line}'"
                        )

                    key = parts[0].strip().upper()
                    value = parts[1].strip()

                    normalized_key = (
                        "OUTPUT_FILE" if key == "OUTPUT" else key
                    )

                    if normalized_key not in self.config:
                        raise ValueError(f"Unsupported key: '{key}'")

                    self.assign_value(normalized_key, value)
                    keys_seen.add(normalized_key.lower())

            missing = [
                k for k in self._REQUIRED_KEYS if k not in keys_seen
            ]
            if missing:
                raise ValueError(
                    "Missing required entries. Make sure all of these "
                    f"are present: {self._REQUIRED_KEYS}"
                )

            if self.validate():
                return Config(
                    width=self.config["WIDTH"],
                    height=self.config["HEIGHT"],
                    entry=self.config["ENTRY"],
                    exit=self.config["EXIT"],
                    output_file=self.config["OUTPUT_FILE"],
                    perfect=bool(self.config["PERFECT"]),
                    seed=self.config["SEED"],
                    animate=bool(self.config["ANIMATE"]),
                    theme=self.config["THEME"],
                    draw_pattern=self._draw_pattern,
                )
        except FileNotFoundError:
            print(f"Error: The file '{self.filepath}' was not found.")
        except PermissionError:
            print(
                f"Error: Can't access '{self.filepath}'. "
                "Make sure you have the required permissions."
            )
        except ValueError as e:
            print(f"Configuration Error: {e}")
        return None

    def assign_value(self, key: str, value: str) -> None:
        """Parse a single key-value pair and store it in self.config.

        Strips surrounding quotes from the value string, then converts it
        to the appropriate Python type for the given key.

        Args:
            key:   The normalised (upper-case) config key.
            value: The raw string value read from the config file.

        Raises:
            ValueError: If the value cannot be converted to the expected
                        type for the given key.
        """
        value = value.strip('"').strip("'")

        try:
            if key == "WIDTH":
                self.config["WIDTH"] = int(value)

            elif key == "HEIGHT":
                self.config["HEIGHT"] = int(value)

            elif key == "ENTRY":
                value = value.strip()

                if value.startswith("(") and value.endswith(")"):
                    value = value[1:-1]

                parts = value.split(",")

                if len(parts) != 2:
                    raise ValueError("ENTRY must have exactly"
                                     "2 coordinates (x,y)")

                self.config["ENTRY"] = (
                    int(parts[0].strip()), int(parts[1].strip())
                )

            elif key == "EXIT":
                value = value.strip()

                if value.startswith("(") and value.endswith(")"):
                    value = value[1:-1]

                parts = value.split(",")

                if len(parts) != 2:
                    raise ValueError(
                        "EXIT must have exactly 2 coordinates (x,y)"
                    )

                self.config["EXIT"] = (
                    int(parts[0].strip()), int(parts[1].strip())
                )

            elif key == "PERFECT":
                lower = value.lower()
                if lower in ("true", "1", "yes"):
                    parsed: Optional[bool] = True
                elif lower in ("false", "0", "no"):
                    parsed = False
                else:
                    parsed = None
                self.config["PERFECT"] = parsed

            elif key == "ANIMATE":
                lower = value.lower()
                if lower in ("true", "1", "yes"):
                    parsed_animate: Optional[bool] = True
                elif lower in ("false", "0", "no"):
                    parsed_animate = False
                else:
                    parsed_animate = None
                self.config["ANIMATE"] = parsed_animate

            elif key == "OUTPUT_FILE":
                self.config["OUTPUT_FILE"] = value

            elif key == "SEED":
                if not value:
                    print("Seed cant be empty")
                    sys.exit()
                self.config["SEED"] = value

            elif key == "THEME":
                self.config["THEME"] = value.lower() if value else "ice"

        except ValueError:
            raise ValueError(f"Could not parse '{value}' for key '{key}'")

    def validate(self) -> bool:
        """Validate all parsed values against business rules.

        Checks dimensions, entry/exit bounds, pattern overlap, boolean
        fields, and output-file constraints.  Also sets self._draw_pattern
        to False when the grid is too small to fit the 42 pattern.

        Returns:
            True if every check passes.

        Raises:
            ValueError: With a descriptive message for the first rule that
                        is violated.
        """
        w = self.config["WIDTH"]
        h = self.config["HEIGHT"]

        if w < 3 or h < 3:
            raise ValueError("WIDTH and HEIGHT must be at least 3.")

        if w > self.MAX_WIDTH or h > self.MAX_HEIGHT:
            raise ValueError(
                f"WIDTH must be <= {self.MAX_WIDTH} and "
                f"HEIGHT must be <= {self.MAX_HEIGHT}."
            )

        self._draw_pattern = True
        if w < self.MIN_WIDTH or h < self.MIN_HEIGHT:
            self._draw_pattern = False
            print(
                f"Note: Maze size ({w}x{h}) is too small to draw the '42'"
            )

        entry = self.config["ENTRY"]
        exit_ = self.config["EXIT"]

        if entry == exit_:
            raise ValueError("ENTRY and EXIT must be different.")

        entry_x, entry_y = entry
        exit_x, exit_y = exit_

        if not (0 <= entry_x < w and 0 <= entry_y < h):
            raise ValueError(
                f"ENTRY ({entry_x},{entry_y}) is outside the {w}x{h} grid."
            )
        if not (0 <= exit_x < w and 0 <= exit_y < h):
            raise ValueError(
                f"EXIT ({exit_x},{exit_y}) is outside the {w}x{h} grid."
            )

        if self._draw_pattern:
            forbidden = set(_pattern_coords(w, h))
            if entry in forbidden:
                raise ValueError(
                    f"ENTRY {entry} overlaps with the 42 pattern."
                )
            if exit_ in forbidden:
                raise ValueError(
                    f"EXIT {exit_} overlaps with the 42 pattern."
                )

        for key in ("PERFECT", "ANIMATE"):
            if self.config[key] is None:
                raise ValueError(
                    f"'{key}' must be boolean (true/false, 1/0, yes/no)"
                )

        output = self.config["OUTPUT_FILE"]

        if not output:
            raise ValueError("OUTPUT_FILE must not be empty.")

        if os.path.isdir(output):
            raise ValueError(f"{output} is a directory.")

        if "." not in os.path.basename(output):
            raise ValueError("OUTPUT_FILE must have extension.")

        if os.path.basename(output) in _PROJECT_FILES:
            raise ValueError("OUTPUT_FILE conflicts with project file.")

        theme = self.config["THEME"]
        if theme not in {"dungeon", "ice", "neon", "forest"}:
            raise ValueError("Invalid theme.")

        return True


def parse_config(filepath: str) -> Optional[Config]:
    """Convenience wrapper — parse a config file and return a Config or None.

    Args:
        filepath: Path to the maze configuration file.

    Returns:
        A validated Config dataclass, or None if parsing or validation failed.
    """
    return ConfigParser(filepath).parse()
