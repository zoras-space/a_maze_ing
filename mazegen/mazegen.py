"""Generate a maze using cardinal wall flags and iterative backtracking."""

import random
from .pattern import get_42_cells
from collections import deque

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

    def __init__(self, x: int, y: int) -> None:
        """Start with all walls closed and the cell unvisited."""
        self.x = x
        self.y = y
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

        self.pattern_cells = get_42_cells(
                width,
                height,
                entry,
                exit_point
                )

        self.maze = self.create_grid()

    def create_grid(self) -> list[list[Cell]]:
        """Create a grid where every cell starts with all walls closed."""
        return [
            [Cell(x, y) for x in range(self.width)]
            for y in range(self.height)
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
                if (nx, ny) not in self.pattern_cells:
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
        """Generate a perfect maze using recursive backtracking."""
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

    def _find_dead_ends(self) -> list[tuple[int, int]]:
        """Return cells that have exactly one open passage."""
        dead_ends: list[tuple[int, int]] = []

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue

                cell = self.maze[y][x]
                open_walls = sum(
                    not cell.has_wall(wall)
                    for wall in DIRECTIONS
                )

                if open_walls == 1:
                    dead_ends.append((x, y))

        return dead_ends

    def _generate_non_perfect(self, rng: random.Random) -> None:
        """Create loops by opening internal walls at dead ends of a tree."""
        self._generate_perfect(rng)

        for x, y in self._find_dead_ends():
            cell = self.maze[y][x]

            open_walls = sum(
                not cell.has_wall(wall)
                for wall in DIRECTIONS
            )

            if open_walls != 1:
                continue

            neighbours: list[tuple[int, int, int]] = []

            for direction, (dx, dy) in DIRECTIONS.items():
                nx, ny = x + dx, y + dy

                if not self._is_inside_maze(nx, ny):
                    continue

                if (nx, ny) in self.pattern_cells:
                    continue

                if cell.has_wall(direction):
                    neighbours.append((nx, ny, direction))

            if neighbours:
                nx, ny, direction = rng.choice(neighbours)

                cell.remove_wall(direction)
                self.maze[ny][nx].remove_wall(OPPOSITE[direction])

    def shortest_path(self) -> str:
        """Return the shortest path from entry to exit."""
        queue: deque[tuple[int, int]] = deque([self.entry])

        previous: dict[
                tuple[int, int],
                tuple[tuple[int, int], str],
        ] = {}

        visited = {self.entry}

        direction_names = {
                NORTH: "N",
                EAST: "E",
                SOUTH: "S",
                WEST: "W",
        }

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.exit_point:
                break

            for wall, (dx, dy) in DIRECTIONS.items():
                nx = x + dx
                ny = y + dy
                next_position = (nx, ny)

                if not self._is_inside_maze(nx, ny):
                    continue

                if next_position in visited:
                    continue

                if self.maze[y][x].has_wall(wall):
                    continue

                visited.add(next_position)

                previous[next_position] = (
                    (x, y),
                    direction_names[wall],
                )

                queue.append(next_position)

        if self.exit_point not in visited:
            raise ValueError("No path exists from entry to exit.")

        path: list[str] = []
        current = self.exit_point

        while current != self.entry:
            parent, move = previous[current]
            path.append(move)
            current = parent

        path.reverse()
        return "".join(path)
