"""Generate a maze using cardinal wall flags and iterative backtracking."""

import random

from .pattern import get_42_cells

from .cell import Cell, DIRECTIONS, OPPOSITE


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
            [Cell() for x in range(self.width)]
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

        self._generate_perfect(rng)
        if not self.perfect:
            from .pacman import _generate_non_perfect

            _generate_non_perfect(
                self.maze, self.width, self.height, self.pattern_cells, rng,
                self.open_passage,
            )

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
            self.open_passage(self.maze[y][x], self.maze[ny][nx], direction)
            self.maze[ny][nx].visited = True
            stack.append((nx, ny))

    def open_passage(self, cell: Cell, neighbour: Cell, direction: int) -> None:
        """Remove both sides of the shared wall between neighbouring cells."""
        cell.remove_wall(direction)
        neighbour.remove_wall(OPPOSITE[direction])

    def shortest_path(self) -> str:
        """Return the shortest path from entry to exit."""
        from .solver import solve_shortest_path

        return solve_shortest_path(self.maze, self.entry, self.exit_point)
