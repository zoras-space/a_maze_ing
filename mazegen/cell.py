"""Provide general operations on maze cells."""

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST

OPPOSITE = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}

DIRECTIONS = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}


class Cell:
    """Store a cell's walls and temporary generation state."""

    def __init__(self) -> None:
        """Start with all walls closed and the cell unvisited."""
        self.walls: int = ALL_WALLS
        self.visited: bool = False

    def has_wall(self, wall: int) -> bool:
        """Return whether the specified wall exists."""
        return bool(self.walls & wall)

    def remove_wall(self, wall: int) -> None:
        """Remove the specified wall."""
        self.walls &= ~wall

    def add_wall(self, wall: int) -> None:
        """Add the specified wall."""
        self.walls |= wall
