from dataclasses import dataclass


@dataclass
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def _parse_bool(value: str) -> bool:
    """Parse boolean value from string."""
    value = value.strip().lower()

    if value in ("true", "1", "yes"):
        return True
    if value in ("false", "0", "no"):
        return False

    raise ValueError(f"Invalid boolean value: {value}")


def _parse_coord(value: str) -> tuple[int, int]:
    """Parse coordinate in format 'x,y'."""
    parts = value.split(",")

    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate format: {value}")

    x = int(parts[0].strip())
    y = int(parts[1].strip())

    return (x, y)


def parse_config(file_path: str) -> Config:
    """
    Parse configuration file.

    Expected format:
        WIDTH=10
        HEIGHT=10
        ENTRY=0,0
        EXIT=9,9
        OUTPUT=maze.txt
        PERFECT=True
        SEED=42 (optional)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {file_path}")

    data: dict[str, str] = {}

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ValueError(f"Invalid line: {line}")

        key, value = line.split("=", 1)
        data[key.strip().upper()] = value.strip()

    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])
        entry = _parse_coord(data["ENTRY"])
        exit_ = _parse_coord(data["EXIT"])
        output_file = data["OUTPUT"]
        perfect = _parse_bool(data["PERFECT"])
        seed = int(data["SEED"]) if "SEED" in data else None
    except KeyError as e:
        raise ValueError(f"Missing required field: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid value: {e}")

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )
