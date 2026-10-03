"""Solve a maze using the existing breadth-first search."""

from collections import deque

from .cell import Cell, DIRECTIONS, NORTH, EAST, SOUTH, WEST


def solve_shortest_path(
    maze: list[list[Cell]],
    entry: tuple[int, int],
    exit_point: tuple[int, int],
) -> str:
    """Return the shortest path from entry to exit."""
    height = len(maze)
    width = len(maze[0])
    queue: deque[tuple[int, int]] = deque([entry])

    previous: dict[
            tuple[int, int],
            tuple[tuple[int, int], str],
    ] = {}

    visited = {entry}

    direction_names = {
            NORTH: "N",
            EAST: "E",
            SOUTH: "S",
            WEST: "W",
    }

    while queue:
        x, y = queue.popleft()

        if (x, y) == exit_point:
            break

        for wall, (dx, dy) in DIRECTIONS.items():
            nx = x + dx
            ny = y + dy
            next_position = (nx, ny)

            if not (0 <= nx < width and 0 <= ny < height):
                continue

            if next_position in visited:
                continue

            if maze[y][x].has_wall(wall):
                continue

            visited.add(next_position)

            previous[next_position] = (
                (x, y),
                direction_names[wall],
            )

            queue.append(next_position)

    if exit_point not in visited:
        raise ValueError("No path exists from entry to exit.")

    path: list[str] = []
    current = exit_point

    while current != entry:
        parent, move = previous[current]
        path.append(move)
        current = parent

    path.reverse()
    return "".join(path)
