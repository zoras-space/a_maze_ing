"""Apply the existing non-perfect maze modifications."""

import random
from collections.abc import Callable

from .cell import Cell, DIRECTIONS, EAST, SOUTH


def _count_open_passages(cell: Cell) -> int:
    """Return the number of open cardinal passages of a cell."""
    return sum(not cell.has_wall(wall) for wall in DIRECTIONS)


def _generate_non_perfect(
    maze: list[list[Cell]],
    width: int,
    height: int,
    pattern_cells: set[tuple[int, int]],
    rng: random.Random,
    open_passage: Callable[[Cell, Cell, int], None],
) -> None:
    """Open required corridors, reduce dead ends, and ensure extra loops."""
    openings = _open_required_corridors(
        maze, width, height, pattern_cells, rng, open_passage
    )
    openings += _reduce_dead_ends(
        maze, width, height, pattern_cells, rng, open_passage
    )
    _ensure_loops(
        maze, width, height, pattern_cells, rng, open_passage, openings
    )


def _open_safe_passage(
    maze: list[list[Cell]],
    width: int,
    height: int,
    pattern_cells: set[tuple[int, int]],
    rng: random.Random,
    open_passage: Callable[[Cell, Cell, int], None],
    x: int,
    y: int,
) -> bool:
    """Open one randomly selected safe closed wall, if one exists."""
    if not (0 <= x < width and 0 <= y < height):
        return False
    if (x, y) in pattern_cells:
        return False

    cell = maze[y][x]
    neighbours: list[tuple[int, int, int]] = []
    for direction, (dx, dy) in DIRECTIONS.items():
        nx, ny = x + dx, y + dy
        if not (0 <= nx < width and 0 <= ny < height):
            continue
        if (nx, ny) in pattern_cells:
            continue
        if not cell.has_wall(direction):
            continue
        if _creates_open_3x3(maze, width, height, x, y, direction):
            continue
        neighbours.append((nx, ny, direction))

    if not neighbours:
        return False
    nx, ny, direction = rng.choice(neighbours)
    open_passage(cell, maze[ny][nx], direction)
    return True


def _open_required_corridors(
    maze: list[list[Cell]],
    width: int,
    height: int,
    pattern_cells: set[tuple[int, int]],
    rng: random.Random,
    open_passage: Callable[[Cell, Cell, int], None],
) -> int:
    """Aim for two passages at each corner and the centre; count openings."""
    openings = 0
    required_cells = (
        (0, 0), (width - 1, 0), (0, height - 1),
        (width - 1, height - 1), (width // 2, height // 2),
    )
    for x, y in required_cells:
        if (x, y) in pattern_cells:
            continue
        while _count_open_passages(maze[y][x]) < 2:
            if not _open_safe_passage(
                maze, width, height, pattern_cells, rng, open_passage, x, y
            ):
                break
            openings += 1
    return openings


def _reduce_dead_ends(
    maze: list[list[Cell]],
    width: int,
    height: int,
    pattern_cells: set[tuple[int, int]],
    rng: random.Random,
    open_passage: Callable[[Cell, Cell, int], None],
) -> int:
    """Reduce dead ends to at most two when safe passages allow it."""
    openings = 0
    while True:
        dead_ends = _find_dead_ends(maze, width, height, pattern_cells)
        if len(dead_ends) <= 2:
            return openings
        changes = 0
        for x, y in dead_ends:
            if _count_open_passages(maze[y][x]) != 1:
                continue
            if _open_safe_passage(
                maze, width, height, pattern_cells, rng, open_passage, x, y
            ):
                changes += 1
        openings += changes
        if not changes:
            return openings


def _ensure_loops(
    maze: list[list[Cell]],
    width: int,
    height: int,
    pattern_cells: set[tuple[int, int]],
    rng: random.Random,
    open_passage: Callable[[Cell, Cell, int], None],
    openings: int,
) -> None:
    """Ensure two extra cycle-producing openings whenever safely possible."""
    if openings >= 2:
        return
    for y in range(height):
        for x in range(width):
            if _open_safe_passage(
                maze, width, height, pattern_cells, rng, open_passage, x, y
            ):
                openings += 1
                if openings >= 2:
                    return


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
            open_walls = _count_open_passages(cell)

            if open_walls == 1:
                dead_ends.append((x, y))

    return dead_ends
