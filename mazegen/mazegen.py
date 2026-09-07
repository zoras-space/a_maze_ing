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
    """representation of one Cell in the maze
       Cell knows which walls it has,
       can add/remove/check walls
       holds temporary state    
    """
    def __init__(self) -> None:
        self.walls: int = ALL_WALLS
        self.visited: bool = False

    def has_wall(self, wall: int) -> bool:
        """checks wall_state"""
        return bool(self.walls & wall)

    def remove_wall(self, wall: int) -> None:
        """removes wall"""
        self.walls &= ~ wall 

    def add_wall(self, wall: int) -> None:
        """adds wall"""
        self.walls |= wall


class MazeGenerator:
    """generate and provide access to the maze"""
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_point: tuple[int, int],
        perfect: bool = False,
        seed: int | None = None
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_point = exit_point
        self.perfect = perfect
        self.seed = seed
        self.maze = self.create_grid()


    def create_grid(self) -> list[list[Cell]]:
        """creates a grid where every cell starts out with all walls closed"""
        return [
        [Cell() for _ in range(self.width)]
        for _ in range(self.height)
        ]


    def _is_inside_maze(self, x: int, y: int) -> bool:
        """check if the coordinates are inside the maze"""
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

