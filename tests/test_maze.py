"""Check the perfect-maze guarantees and ASCII wall rendering."""

import unittest

from display.ascii_renderer import render_ascii
from mazegen import MazeGenerator
from mazegen.pacman import _find_dead_ends
from mazegen.cell import DIRECTIONS, EAST, OPPOSITE, SOUTH


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
                    self.assertEqual(len(reached), width * height)
                    # A connected graph with V - 1 edges is a tree.
                    self.assertEqual(passages, width * height - 1)

    def test_seed_reproducibility(self) -> None:
        """Check repeated generation and independence from endpoint markers."""
        first = MazeGenerator(10, 8, (0, 0), (9, 7), True, 42)
        second = MazeGenerator(10, 8, (3, 2), (4, 5), True, 42)
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
            render_ascii(horizontal), "+---+---+\n| E   X |\n+---+---+"
        )
        self.assertEqual(before, [cell.walls for cell in horizontal.maze[0]])
        vertical = MazeGenerator(1, 2, (0, 0), (0, 1), True, 0)
        vertical.generate()
        self.assertEqual(
            render_ascii(vertical), "+---+\n| E |\n+   +\n| X |\n+---+"
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
        for width, height in ((1, 1), (1, 8), (10, 1), (2, 2), (10, 8)):
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
                    self.assertEqual(len(reached), width * height)
                    if width > 1 and height > 1:
                        self.assertGreater(passages, width * height - 1)
                    else:
                        self.assertEqual(passages, width * height - 1)
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


if __name__ == "__main__":
    unittest.main()
