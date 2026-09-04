NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST

class Cell:
    """representation of one Cell in the maze"""
    def __init__(self) -> None:
        self.walls: int = ALL_WALLS
        self.visited: bool = False


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
        self.enrty = entry
        self.exit_point = exit_point
        self.perfect = perfect
        self.seed = seed
        self.maze: list[list[Cell]]
