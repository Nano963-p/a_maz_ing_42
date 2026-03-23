from dataclasses import dataclass


@dataclass
class Cell:
    """Represent one maze cell with wall and generation state."""

    north: bool = True
    east: bool = True
    south: bool = True
    west: bool = True
    visited: bool = False
