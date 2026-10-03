"""Apply the existing non-perfect maze modifications."""

import random
from collections.abc import Callable

from .cell import Cell, DIRECTIONS, EAST, SOUTH


def _generate_non_perfect(
    maze: list[list[Cell]],
    width: int,
    height: int,
    pattern_cells: set[tuple[int, int]],
    rng: random.Random,
    open_passage: Callable[[Cell, Cell, int], None],
) -> None:
    """Create loops by opening internal walls at dead ends of a tree."""
    for x, y in _find_dead_ends(maze, width, height, pattern_cells):
        cell = maze[y][x]

        open_walls = sum(
            not cell.has_wall(wall)
            for wall in DIRECTIONS
        )

        if open_walls != 1:
            continue

        neighbours: list[tuple[int, int, int]] = []

        for direction, (dx, dy) in DIRECTIONS.items():
            nx, ny = x + dx, y + dy

            if not (0 <= nx < width and 0 <= ny < height):
                continue

            if (nx, ny) in pattern_cells:
                continue

            if _creates_open_3x3(maze, width, height, x, y, direction):
                continue

            if cell.has_wall(direction):
                neighbours.append((nx, ny, direction))

        if neighbours:
            nx, ny, direction = rng.choice(neighbours)

            open_passage(cell, maze[ny][nx], direction)


def _creates_open_3x3(
    maze: list[list[Cell]],
    width: int,
    height: int,
    x: int,
    y: int,
    direction: int,
) -> bool:
    """Check whether removing this wall would create an open 3x3 area."""
    dx, dy = DIRECTIONS[direction]
    nx, ny = x + dx, y + dy
    if not ((0 <= x < width and 0 <= y < height)
            and (0 <= nx < width and 0 <= ny < height)):
        return False

    # Inspect shared walls once, treating the proposed wall as open.
    candidate = (min(x, nx), min(y, ny), EAST if dx else SOUTH)
    for top in range(max(0, y - 2), min(y, height - 3) + 1):
        for left in range(max(0, x - 2), min(x, width - 3) + 1):
            if not (left <= nx < left + 3 and top <= ny < top + 3):
                continue
            if all(
                (cx, cy, wall) == candidate
                or not maze[cy][cx].has_wall(wall)
                for wall, columns, rows in (
                    (EAST, 2, 3), (SOUTH, 3, 2)
                )
                for cy in range(top, top + rows)
                for cx in range(left, left + columns)
            ):
                return True
    return False


def _find_dead_ends(
    maze: list[list[Cell]],
    width: int,
    height: int,
    pattern_cells: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Return cells that have exactly one open passage."""
    dead_ends: list[tuple[int, int]] = []

    for y in range(height):
        for x in range(width):
            if (x, y) in pattern_cells:
                continue

            cell = maze[y][x]
            open_walls = sum(
                not cell.has_wall(wall)
                for wall in DIRECTIONS
            )

            if open_walls == 1:
                dead_ends.append((x, y))

    return dead_ends
