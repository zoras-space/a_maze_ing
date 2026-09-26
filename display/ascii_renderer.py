"""Render the existing maze wall data as plain ASCII."""

from mazegen import MazeGenerator
from mazegen.mazegen import EAST, NORTH, SOUTH, WEST


def render_ascii(generator: MazeGenerator) -> str:
    """Return a maze drawing with E/X markers (EX if they share a cell)."""
    lines = []
    top = "+"
    for cell in generator.maze[0]:
        top += ("---" if cell.has_wall(NORTH) else "   ") + "+"
    lines.append(top)

    for y, row in enumerate(generator.maze):
        middle = "|" if row[0].has_wall(WEST) else " "
        bottom = "+"
        for x, cell in enumerate(row):
            marker = ""
            if (x, y) == generator.entry:
                marker += "E"
            if (x, y) == generator.exit_point:
                marker += "X"
            middle += marker.center(3)
            middle += "|" if cell.has_wall(EAST) else " "
            bottom += ("---" if cell.has_wall(SOUTH) else "   ") + "+"
        lines.append(middle)
        lines.append(bottom)

    return "\n".join(lines)
