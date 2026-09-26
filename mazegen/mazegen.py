"""Generate a maze using cardinal wall flags and iterative backtracking."""

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


class MazeGenerator:
    """Generate a maze and expose its cells through maze[y][x]."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_point: tuple[int, int],
        perfect: bool = False,
        seed: int | None = None
    ) -> None:
        """Store settings and create a closed grid with valid endpoints."""
        if width <= 0 or height <= 0:
            raise ValueError("Maze width and height must be positive.")
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_point = exit_point
        self.perfect = perfect
        self.seed = seed
        if not self._is_inside_maze(*entry):
            raise ValueError("Entry must be inside the maze.")
        if not self._is_inside_maze(*exit_point):
            raise ValueError("Exit must be inside the maze.")
        self.maze = self.create_grid()

    def create_grid(self) -> list[list[Cell]]:
        """Create a grid where every cell starts with all walls closed."""
        return [
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _is_inside_maze(self, x: int, y: int) -> bool:
        """Return whether the coordinates are inside the maze."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _get_neighbours(
            self,
            x: int,
            y: int,
        ) -> list[tuple[int, int, int]]:
        """Return valid neighbouring cells and their direction."""
        neighbours: list[tuple[int, int, int]] = []

        for direction, (dx, dy) in DIRECTIONS.items():
            nx = x + dx
            ny = y + dy

            if self._is_inside_maze(nx, ny):
                neighbours.append((nx, ny, direction))

        return neighbours

