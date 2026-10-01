"""Generate a maze using cardinal wall flags and iterative backtracking."""

import random

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
        """Return unvisited neighbouring coordinates and their direction."""
        neighbours: list[tuple[int, int, int]] = []

        for direction, (dx, dy) in DIRECTIONS.items():
            nx = x + dx
            ny = y + dy

            if self._is_inside_maze(nx, ny):
                if not self.maze[ny][nx].visited:
                    neighbours.append((nx, ny, direction))

        return neighbours

    def generate(self) -> None:
        """Generate either a perfect or non-perfect maze."""
        self.maze = self.create_grid()
        rng = random.Random(self.seed)

        if self.perfect:
            self._generate_perfect(rng)
        else:
            self._generate_non_perfect(rng)

    def _generate_perfect(self, rng: random.Random) -> None:
        """Generate a perfect maze using iterative backtracking."""
        self.maze[0][0].visited = True
        stack = [(0, 0)]

        while stack:
            x, y = stack[-1]
            neighbours = self._get_neighbours(x, y)
            if not neighbours:
                stack.pop()
                continue

            nx, ny, direction = rng.choice(neighbours)
            self.maze[y][x].remove_wall(direction)
            self.maze[ny][nx].remove_wall(OPPOSITE[direction])
            self.maze[ny][nx].visited = True
            stack.append((nx, ny))


    def _generate_non_perfect(self, rng: random.Random) -> None:
        """Create loops by opening internal walls at dead ends of a tree."""
        self._generate_perfect(rng)

        for x, y in self._find_dead_ends():
            cell = self.maze[y][x]
            if sum(not cell.has_wall(wall) for wall in DIRECTIONS) != 1:
                continue

            neighbours = []
            for direction, (dx, dy) in DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if self._is_inside_maze(nx, ny) and cell.has_wall(direction):
                    neighbours.append((nx, ny, direction))

            if neighbours:
                nx, ny, direction = rng.choice(neighbours)
                cell.remove_wall(direction)
                self.maze[ny][nx].remove_wall(OPPOSITE[direction])

    def _find_dead_ends(self) -> list[tuple[int, int]]:
        """Return coordinates of cells with exactly one open passage."""
        dead_ends: list[tuple[int, int]] = []

        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                open_sides = 0

                for direction in DIRECTIONS:
                    if not cell.has_wall(direction):
                        open_sides += 1

                if open_sides == 1:
                    dead_ends.append((x, y))
        return dead_ends
