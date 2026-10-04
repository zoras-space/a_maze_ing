"""Check the perfect-maze guarantees and ASCII wall rendering."""

import random
import re
import unittest

from display.ascii_renderer import render_ascii
from mazegen import MazeGenerator
from mazegen.pacman import (
    _count_open_passages, _ensure_loops, _find_dead_ends,
    _open_safe_passage, _reduce_dead_ends,
)
from mazegen.cell import (
    ALL_WALLS, Cell, DIRECTIONS, EAST, OPPOSITE, SOUTH,
)


class MazeTests(unittest.TestCase):
    """Exercise generation independently of the config parser."""

    def test_perfect_maze_properties(self) -> None:
        """Check borders, shared walls, connectivity, and absence of loops."""
        for width, height in ((1, 1), (1, 8), (10, 1), (10, 8), (40, 40)):
            for seed in (0, 42, 123):
                with self.subTest(width=width, height=height, seed=seed):
                    maze = MazeGenerator(
                        width, height, (0, 0), (width - 1, height - 1),
                        perfect=True, seed=seed,
                    )
                    maze.generate()
                    passages = 0
                    for y, row in enumerate(maze.maze):
                        for x, cell in enumerate(row):
                            if (x, y) in maze.pattern_cells:
                                self.assertEqual(cell.walls, ALL_WALLS)
                                self.assertFalse(cell.visited)
                            else:
                                self.assertTrue(cell.visited)
                            for wall, (dx, dy) in DIRECTIONS.items():
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < width and 0 <= ny < height:
                                    other = maze.maze[ny][nx]
                                    self.assertEqual(
                                        cell.has_wall(wall),
                                        other.has_wall(OPPOSITE[wall]),
                                    )
                                    if wall in (EAST, SOUTH):
                                        if not cell.has_wall(wall):
                                            passages += 1
                                else:
                                    self.assertTrue(cell.has_wall(wall))

                    reached = {(0, 0)}
                    pending = [(0, 0)]
                    while pending:
                        x, y = pending.pop()
                        for wall, (dx, dy) in DIRECTIONS.items():
                            if not maze.maze[y][x].has_wall(wall):
                                neighbour = (x + dx, y + dy)
                                if neighbour not in reached:
                                    reached.add(neighbour)
                                    pending.append(neighbour)
                    self.assertEqual(
                        len(reached), width * height - len(maze.pattern_cells)
                    )
                    # A connected graph with V - 1 edges is a tree.
                    self.assertEqual(passages, width * height - len(maze.pattern_cells) - 1)

    def test_seed_reproducibility(self) -> None:
        """Check repeated generation and independence from endpoint markers."""
        first = MazeGenerator(8, 4, (0, 0), (7, 3), True, 42)
        second = MazeGenerator(8, 4, (3, 2), (4, 3), True, 42)
        first.generate()
        second.generate()
        expected = [[cell.walls for cell in row] for row in first.maze]
        self.assertEqual(
            expected, [[cell.walls for cell in row] for row in second.maze]
        )
        first.generate()
        self.assertEqual(
            expected, [[cell.walls for cell in row] for row in first.maze]
        )

    def test_ascii(self) -> None:
        """Check horizontal and vertical passages and unchanged wall data."""
        horizontal = MazeGenerator(2, 1, (0, 0), (1, 0), True, 0)
        horizontal.generate()
        before = [cell.walls for cell in horizontal.maze[0]]
        self.assertEqual(
            re.sub(r"\x1b\[[0-9;]*m", "", render_ascii(horizontal)), "+---+---+\n| E   X |\n+---+---+"
        )
        self.assertEqual(before, [cell.walls for cell in horizontal.maze[0]])
        vertical = MazeGenerator(1, 2, (0, 0), (0, 1), True, 0)
        vertical.generate()
        self.assertEqual(
            re.sub(r"\x1b\[[0-9;]*m", "", render_ascii(vertical)), "+---+\n| E |\n+   +\n| X |\n+---+"
        )

    def test_invalid_settings(self) -> None:
        """Reject invalid dimensions and endpoints."""
        for width, height, entry, exit_point in (
            (0, 2, (0, 0), (0, 1)),
            (2, -1, (0, 0), (1, 0)),
            (2, 2, (-1, 0), (1, 1)),
            (2, 2, (0, 0), (2, 1)),
        ):
            with self.assertRaises(ValueError):
                MazeGenerator(width, height, entry, exit_point, True)

    def test_non_perfect_maze_properties(self) -> None:
        """Check loops, connectivity, shared walls, and closed borders."""
        for width, height in ((1, 1), (1, 8), (10, 1), (2, 2), (2, 3),
                              (3, 3), (8, 4), (10, 8), (20, 15), (40, 40)):
            for seed in (0, 42, 123):
                with self.subTest(width=width, height=height, seed=seed):
                    maze = MazeGenerator(
                        width, height, (0, 0), (width - 1, height - 1),
                        seed=seed,
                    )
                    maze.generate()
                    passages = 0
                    for y, row in enumerate(maze.maze):
                        for x, cell in enumerate(row):
                            if (x, y) in maze.pattern_cells:
                                self.assertEqual(cell.walls, ALL_WALLS)
                                self.assertFalse(cell.visited)
                            else:
                                self.assertTrue(cell.visited)
                            for wall, (dx, dy) in DIRECTIONS.items():
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < width and 0 <= ny < height:
                                    self.assertEqual(
                                        cell.has_wall(wall),
                                        maze.maze[ny][nx].has_wall(OPPOSITE[wall]),
                                    )
                                    if wall in (EAST, SOUTH):
                                        passages += not cell.has_wall(wall)
                                else:
                                    self.assertTrue(cell.has_wall(wall))

                    reached = {(0, 0)}
                    pending = [(0, 0)]
                    while pending:
                        x, y = pending.pop()
                        for wall, (dx, dy) in DIRECTIONS.items():
                            if not maze.maze[y][x].has_wall(wall):
                                neighbour = (x + dx, y + dy)
                                if neighbour not in reached:
                                    reached.add(neighbour)
                                    pending.append(neighbour)
                    self.assertEqual(
                        len(reached), width * height - len(maze.pattern_cells)
                    )
                    if width > 1 and height > 1:
                        self.assertGreater(passages, width * height - len(maze.pattern_cells) - 1)
                    else:
                        self.assertEqual(passages, width * height - len(maze.pattern_cells) - 1)
                    expected = [[cell.walls for cell in row] for row in maze.maze]
                    maze.generate()
                    self.assertEqual(
                        expected, [[cell.walls for cell in row] for row in maze.maze]
                    )

    def test_find_dead_ends(self) -> None:
        """Count each dead end once and exclude cells with two passages."""
        maze = MazeGenerator(3, 1, (0, 0), (2, 0), True, 42)
        maze.generate()
        self.assertEqual(_find_dead_ends(
            maze.maze, maze.width, maze.height, maze.pattern_cells
        ), [(0, 0), (2, 0)])


    def test_pacman_corridors_loops_and_dead_ends(self) -> None:
        """Check normal boards meet corridor, loop, and dead-end targets."""
        for width, height in ((8, 4), (20, 15), (40, 40)):
            for seed in range(20):
                with self.subTest(width=width, height=height, seed=seed):
                    maze = MazeGenerator(
                        width, height, (0, 0), (width - 1, height - 1),
                        seed=seed,
                    )
                    maze.generate()
                    required = (
                        (0, 0), (width - 1, 0), (0, height - 1),
                        (width - 1, height - 1), (width // 2, height // 2),
                    )
                    for x, y in required:
                        if (x, y) not in maze.pattern_cells:
                            self.assertGreaterEqual(
                                _count_open_passages(maze.maze[y][x]), 2
                            )
                    self.assertLessEqual(len(_find_dead_ends(
                        maze.maze, width, height, maze.pattern_cells
                    )), 2)
                    passages = sum(
                        not cell.has_wall(wall)
                        for row in maze.maze for cell in row
                        for wall in (EAST, SOUTH)
                    )
                    vertices = width * height - len(maze.pattern_cells)
                    self.assertGreaterEqual(passages, vertices - 1 + 2)

    def test_no_open_3x3(self) -> None:
        """Scan every 3x3 block independently of the generation guard."""
        for width, height in ((3, 3), (4, 4), (10, 8), (20, 15)):
            for seed in range(20):
                maze = MazeGenerator(
                    width, height, (0, 0), (width - 1, height - 1),
                    seed=seed,
                )
                maze.generate()
                for top in range(height - 2):
                    for left in range(width - 2):
                        walls = [
                            maze.maze[y][x].has_wall(EAST)
                            for y in range(top, top + 3)
                            for x in range(left, left + 2)
                        ] + [
                            maze.maze[y][x].has_wall(SOUTH)
                            for y in range(top, top + 2)
                            for x in range(left, left + 3)
                        ]
                        self.assertTrue(any(walls),
                                        (width, height, seed, left, top))

    def test_safe_opening_and_loop_fallback(self) -> None:
        """Check callback use, blocked sources, and tiny loop capacity."""
        maze = MazeGenerator(2, 3, (0, 0), (1, 2), True, 42)
        maze.generate()
        args = (maze.maze, 2, 3, maze.pattern_cells, random.Random(42))
        calls: list[int] = []

        def open_passage(
            cell: Cell, neighbour: Cell, direction: int,
        ) -> None:
            calls.append(direction)
            maze.open_passage(cell, neighbour, direction)

        _ensure_loops(*args, open_passage, 0)
        self.assertEqual(len(calls), 2)
        _ensure_loops(*args, open_passage, 2)
        self.assertEqual(len(calls), 2)
        self.assertFalse(_open_safe_passage(*args, open_passage, -1, 0))
        maze.pattern_cells.add((0, 0))
        self.assertFalse(_open_safe_passage(*args, open_passage, 0, 0))

        tiny = MazeGenerator(2, 2, (0, 0), (1, 1), True, 42)
        tiny.generate()
        _ensure_loops(tiny.maze, 2, 2, set(), random.Random(42),
                      tiny.open_passage, 0)
        self.assertEqual(sum(
            not cell.has_wall(wall)
            for row in tiny.maze for cell in row for wall in (EAST, SOUTH)
        ), 4)

    def test_blocked_dead_ends_stop(self) -> None:
        """Stop when pattern and border constraints prevent any changes."""
        maze = MazeGenerator(3, 3, (0, 0), (2, 2), True, 42)
        pattern = {(0, 0), (2, 0), (0, 2), (2, 2)}
        for direction, (dx, dy) in DIRECTIONS.items():
            maze.open_passage(maze.maze[1][1],
                              maze.maze[1 + dy][1 + dx], direction)
        before = [[cell.walls for cell in row] for row in maze.maze]
        self.assertEqual(_reduce_dead_ends(
            maze.maze, 3, 3, pattern, random.Random(42), maze.open_passage
        ), 0)
        self.assertEqual(len(_find_dead_ends(maze.maze, 3, 3, pattern)), 4)
        self.assertEqual(before,
                         [[cell.walls for cell in row] for row in maze.maze])

    def test_safe_opening_rejects_open_3x3(self) -> None:
        """Keep the last wall in an otherwise fully open 3x3 block."""
        maze = MazeGenerator(3, 3, (0, 0), (2, 2), True, 42)
        for y in range(3):
            for x in range(3):
                for wall in (EAST, SOUTH):
                    dx, dy = DIRECTIONS[wall]
                    if x + dx < 3 and y + dy < 3:
                        maze.open_passage(
                            maze.maze[y][x], maze.maze[y + dy][x + dx], wall
                        )
        maze.maze[1][1].add_wall(EAST)
        maze.maze[1][2].add_wall(OPPOSITE[EAST])
        before = [[cell.walls for cell in row] for row in maze.maze]
        self.assertFalse(_open_safe_passage(
            maze.maze, 3, 3, set(), random.Random(42), maze.open_passage, 1, 1
        ))
        self.assertEqual(before,
                         [[cell.walls for cell in row] for row in maze.maze])


if __name__ == "__main__":
    unittest.main()
