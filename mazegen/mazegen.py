NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST

class Cell:
    """representation of one Cell in the maze
       Cell knows which walls it has,
       can add/remove/check walls
       holds temporary state    
    """
    def __init__(self) -> None:
        self.walls: int = ALL_WALLS
        self.visited: bool = False

    def has_wall(self, wall) -> bool:
        """checks wall_state"""

    def remove_wall(self, wall) -> None:
        """removes wall"""

    def add_wall(self, wall) -> None:
        """adds wall"""


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
