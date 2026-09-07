from typing import Protocol


class CellLike(Protocol):
    walls: int


def write_output(filename: str, content: str) -> None:
    with open(filename, "w") as file:
        file.write(content)


def encode_cell(walls: int) -> str:
    return format(walls, "X")


def encode_maze(maze: list[list[CellLike]]) -> list[str]:
    rows = []

    for row in maze:
        encoded_row = ""

        for cell in row:
            encoded_row += encode_cell(cell.walls)

        rows.append(encoded_row)

    return rows


def validate_hex_row(row: str, width: int) -> None:
    if len(row) != width:
        raise ValueError("Invalid row width")

    if not all(char in "0123456789ABCDEF" for char in row):
        raise ValueError("Invalid hexidecimal value")


def validate_hex_maze(rows: list[str], width: int, height: int) -> None:
    if len(rows) != height:
        raise ValueError("Invalid maze height")

    for row in rows:
        validate_hex_row(row, width)


def validate_position(
        position: tuple[int, int],
        width: int,
        height: int
        ) -> None:
    x, y = position

    if not (0 <= x < width and 0 <= y < height):
        raise ValueError("Position is outside the maze")


def validate_entry_exit(
        entry: tuple[int, int],
        exit_pos: tuple[int, int]
        ) -> None:
    if entry == exit_pos:
        raise ValueError("ENTRY and EXIT must be different")


def validate_path(path: str) -> None:
    if not path:
        raise ValueError("Path cannot be empty")

    if not all(move in "NESW" for move in path):
        raise ValueError("Invalid Path")


def parse_position(line: str) -> tuple[int, int]:
    try:
        x, y = line.split(",")
        return int(x), int(y)
    except ValueError:
        raise ValueError("Invalid position format")


def validate_formatted_output(
        content: str,
        width: int,
        height: int
        ) -> None:
    if not content.endswith("\n"):
        raise ValueError("Output must end witha newline")

    sections = content.split("\n\n")

    if len(sections) != 2:
        raise ValueError("Invalid output format")

    maze_lines = sections[0].split("\n")
    info_lines = sections[1].splitlines()

    if len(maze_lines) != height:
        raise ValueError("Invalid maze height")

    if len(info_lines) != 3:
        raise ValueError("Invalid output information")

    entry = parse_position(info_lines[0])
    exit_pos = parse_position(info_lines[1])
    path = info_lines[2]

    validate_output(maze_lines, width, height, entry, exit_pos, path)


def validate_output(
        rows: list[str],
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        path: str
        ) -> None:
    validate_hex_maze(rows, width, height)
    validate_position(entry, width, height)
    validate_position(exit_pos, width, height)
    validate_entry_exit(entry, exit_pos)
    validate_path(path)


def format_hex_maze(rows: list[str]) -> str:
    return "\n".join(rows)


def format_output(
        rows: list[str],
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        path: str
        ) -> str:
    output = format_hex_maze(rows)
    output += "\n\n"
    output += f"{entry[0]}, {entry[1]}\n"
    output += f"{exit_pos[0]}, {exit_pos[1]}\n"
    output += f"{path}\n"

    return output


def generate_output(
        maze: list[list[CellLike]],
        filename: str,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        path: str
        ) -> None:
    rows = encode_maze(maze)
    content = format_output(rows, entry, exit_pos, path)
    write_output(filename, content)
