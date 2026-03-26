from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    animate: bool = False
    hallucination: bool = False
    theme: str = "dungeon"


class ConfigParser:
    _DEFAULTS: Dict[str, object] = {
        "WIDTH": 0,
        "HEIGHT": 0,
        "ENTRY": (0, 0),
        "EXIT": (0, 0),
        "OUTPUT_FILE": "output_maze.txt",
        "PERFECT": False,
        "ANIMATE": False,
        "SEED": None,
        "HALLUCINATION": False,
        "THEME": "dungeon",
    }

    _REQUIRED_KEYS = [
        "width", "height", "entry", "exit", "output_file", "perfect"
    ]

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.config: Dict[str, object] = dict(self._DEFAULTS)

    def parse(self) -> Optional[Config]:
        keys_seen: set[str] = set()
        try:
            with open(self.filepath, 'r', encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split('=', 1)
                    if len(parts) < 2:
                        raise ValueError(f"Invalid line (missing '='): '{line}'")

                    key = parts[0].strip().upper()
                    value = parts[1].strip()

                    normalized_key = "OUTPUT_FILE" if key == "OUTPUT" else key

                    if normalized_key not in self.config:
                        raise ValueError(f"Unsupported key: '{key}'")

                    self.assign_value(normalized_key, value)
                    keys_seen.add(normalized_key.lower())

            missing = [k for k in self._REQUIRED_KEYS if k not in keys_seen]
            if missing:
                raise ValueError(
                    "Missing required entries. Make sure all of these "
                    f"are present: {self._REQUIRED_KEYS}"
                )

            if self.validate():
                return Config(
                    width=int(self.config["WIDTH"]),
                    height=int(self.config["HEIGHT"]),
                    entry=self.config["ENTRY"],  # type: ignore[arg-type]
                    exit=self.config["EXIT"],  # type: ignore[arg-type]
                    output_file=str(self.config["OUTPUT_FILE"]),
                    perfect=bool(self.config["PERFECT"]),
                    seed=self.config["SEED"],  # type: ignore[arg-type]
                    animate=bool(self.config["ANIMATE"]),
                    hallucination=bool(self.config["HALLUCINATION"]),
                    theme=str(self.config["THEME"]),
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
        try:
            if key in ("WIDTH", "HEIGHT"):
                self.config[key] = int(value)
            elif key in ("ENTRY", "EXIT"):
                parts = value.split(',')
                if len(parts) != 2:
                    raise ValueError(f"{key} must have exactly 2 coordinates (x,y)")
                self.config[key] = (int(parts[0].strip()), int(parts[1].strip()))
            elif key in ("PERFECT", "ANIMATE", "HALLUCINATION"):
                lower = value.lower()
                if lower in ("true", "1", "yes"):
                    self.config[key] = True
                elif lower in ("false", "0", "no"):
                    self.config[key] = False
                else:
                    self.config[key] = None
            elif key == "OUTPUT_FILE":
                self.config[key] = value
            elif key == "SEED":
                self.config[key] = int(value)
            elif key == "THEME":
                self.config[key] = value.lower()
        except ValueError:
            raise ValueError(f"Could not parse '{value}' for key '{key}'")

    def validate(self) -> bool:
        w = int(self.config["WIDTH"])
        h = int(self.config["HEIGHT"])
        if w < 9 or h < 7:
            raise ValueError(
                "WIDTH must be >= 9 and HEIGHT must be >= 7 to fit the 42 pattern."
            )

        entry: tuple[int, int] = self.config["ENTRY"]  # type: ignore
        exit_: tuple[int, int] = self.config["EXIT"]  # type: ignore
        if entry == exit_:
            raise ValueError("ENTRY and EXIT must be different.")

        entry_x, entry_y = entry
        exit_x, exit_y = exit_
        if not (0 <= entry_x < w and 0 <= entry_y < h):
            raise ValueError(f"ENTRY ({entry_x},{entry_y}) is outside the {w}x{h} grid.")
        if not (0 <= exit_x < w and 0 <= exit_y < h):
            raise ValueError(f"EXIT ({exit_x},{exit_y}) is outside the {w}x{h} grid.")

        for key in ("PERFECT", "ANIMATE", "HALLUCINATION"):
            if self.config[key] is None:
                raise ValueError(
                    f"'{key}' must be a boolean (accepted values: true/false, 1/0, yes/no)."
                )

        output = str(self.config["OUTPUT_FILE"])
        if not output:
            raise ValueError("OUTPUT_FILE must not be empty.")
        if output in {'.', '..', './', '../', '/'}:
            raise ValueError("OUTPUT_FILE looks like a directory path instead of a filename.")

        theme = str(self.config["THEME"])
        if theme not in {"dungeon", "ice", "neon", "forest"}:
            raise ValueError("THEME must be one of: dungeon, ice, neon, forest.")

        return True


def parse_config(filepath: str) -> Optional[Config]:
    return ConfigParser(filepath).parse()
