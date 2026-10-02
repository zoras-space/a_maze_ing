"""Render the existing maze wall data as plain ASCII."""

from mazegen import MazeGenerator
from mazegen.mazegen import EAST, NORTH, SOUTH, WEST


YELLOW_BG = "\033[43m"
RESET = "\033[0m"

WALL_COLOURS = {
        "white": "\033[37m",
        "blue": "\033[34m",
        "green": "\033[32m",
        "red": "\033[31m",
        "cyan": "\033[36m",
}

DEFAULT_WALL_COLOUR = "white"


def render_ascii(
    generator: MazeGenerator,
    path: str = "",
    show_path: bool = False,
    wall_colour: str = DEFAULT_WALL_COLOUR,
) -> str:
    """Return a maze drawing with optional path and wall colour."""
    lines = []

    colour = WALL_COLOURS.get(
        wall_colour,
        WALL_COLOURS[DEFAULT_WALL_COLOUR],
    )

    path_cells: set[tuple[int, int]] = set()

    if show_path and path:
        x, y = generator.entry
        path_cells.add((x, y))

        directions = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        for move in path:
            dx, dy = directions[move]
            x += dx
            y += dy
            path_cells.add((x, y))

    top = colour + "+"

    for cell in generator.maze[0]:
        top += ("---" if cell.has_wall(NORTH) else "   ") + "+"

    top += RESET
    lines.append(top)

    for y, row in enumerate(generator.maze):
        middle = RESET
        middle += (
            colour + "|"
            if row[0].has_wall(WEST)
            else " "
        )

        bottom = colour + "+"

        for x, cell in enumerate(row):
            marker = ""

            if (x, y) == generator.entry:
                marker += "E"

            if (x, y) == generator.exit_point:
                marker += "X"

            if (x, y) in generator.pattern_cells:
                middle += YELLOW_BG + "   " + RESET

            elif (x, y) in path_cells:
                if (x, y) == generator.entry:
                    middle += RESET + marker.center(3)
                elif (x, y) == generator.exit_point:
                    middle += RESET + marker.center(3)
                else:
                    middle += RESET + "*".center(3)

            else:
                middle += marker.center(3)

            middle += (
                colour + "|" + RESET
                if cell.has_wall(EAST)
                else " "
            )

            bottom += ("---" if cell.has_wall(SOUTH) else "   ") + "+"

        middle += RESET
        bottom += RESET

        lines.append(middle)
        lines.append(bottom)

    return "\n".join(lines)
