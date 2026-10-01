"""Handle the 42 Pattern inside the maze."""

Pattern = (
    "#..#.####",
    "#..#....#",
    "####.####",
    "...#.#...",
    "...#.####",
    )


def get_42_cells(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_point: tuple[int, int]
) -> set[tuple[int, int]]:
    """Return the maze cells that form the 42 pattern."""

    pattern_height = len(Pattern)
    pattern_width = len(Pattern[0])

    if width < pattern_width or height < pattern_height:
        print("42 pattern ommited: maze is too small")
        return set()

    start_x = (width - pattern_width) // 2
    start_y = (height - pattern_height) // 2

    pattern_cells: set[tuple[int, int]] = set()

    for y, row in enumerate(Pattern):
        for x, cell in enumerate(row):
            if cell == "#":
                pattern_cells.add((start_x + x, start_y + y))

    if entry in pattern_cells or exit_point in pattern_cells:
        raise ValueError("42 pattern overlaps entry or exit")

    return pattern_cells
