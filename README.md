*This project has been created as part of the 42 curriculum by zodzykon and ntsvuura.*

# A-Maze-ing

## Description

A-Maze-ing is a 42 Berlin project for generating mazes in Python. Each cell
stores its four cardinal walls. It generates perfect mazes with exactly one
path between any two cells, or non-perfect mazes with additional loops.
The basic terminal ASCII display helps us inspect and test generation.

## Current Status

Currently implemented:

- Configuration parsing and basic validation of required keys, values,
  dimensions, and entry/exit positions.
- Cell walls represented by bit flags.
- Perfect maze generation using randomized depth-first search (DFS) with an
  explicit backtracking stack.
- Non-perfect generation by opening internal walls at dead ends. Single-row
  and single-column grids cannot contain loops.
- Seeded generation through the Python constructor.
- Matching shared walls, closed outside borders, and full connectivity.
- Minimal ASCII rendering and automated generation/rendering tests.
- Readable command-line errors for invalid configuration.

## Implemented Features:

- Pac-Man-specific non-perfect maze generation and the 42 pattern.
- Shortest-path calculation using Breadth First search (BFS).
- Required hexadecimal maze outputand entry/exit/path information.
- Interactive terminal controls for amze generation, shortest path visibility and wall-colours.
- ASCII maze visualisation with entry,exit, solution path and 42 pattern.
- Reusable `mazegen-*` Python Package with wheel and source distribution builds.

Known limitations: the parser does not accept a seed. Its missing-key validation
can raise `KeyError` before completing its checks; the main program catches this
and reports the missing key. This is an initial milestone, not a finished subject
submission.

## Project Structure

```text
.
├── .gitignore
├── README.md
├── a_maze_ing.py
├── config.txt
├── parser.py
├── mazegen/
│   ├── __init__.py
│   └── mazegen.py
├── display/
│   ├── __init__.py
│   └── ascii_renderer.py
└── tests/
    └── test_maze.py
```

Git metadata and generated Python caches are omitted.

- `a_maze_ing.py`: connects configuration, generation, and display.
- `parser.py`: the teammate's existing configuration parser and validation.
- `config.txt`: supplied 20×15 perfect-maze configuration.
- `mazegen/mazegen.py`: wall constants, `Cell`, and `MazeGenerator`.
- `mazegen/__init__.py`: exposes `MazeGenerator` for imports.
- `display/ascii_renderer.py`: reads cell walls and returns an ASCII string.
- `tests/test_maze.py`: checks maze properties, seeds, rendering, and errors.

## How to Run

Use Python 3.10 or newer. No third-party runtime dependencies are required.
From the repository root, run:

```bash
python3 a_maze_ing.py config.txt
```

The maze is printed to the terminal. You can replace `config.txt` with another
configuration filename. For a small example, save the configuration below as
`small.txt`, then run:

```bash
python3 a_maze_ing.py small.txt
```

## Configuration

Use one `KEY=value` per line. All six keys below are required. Blank lines and
whole-line comments beginning with `#` are ignored. Keys are uppercase; avoid
spaces around `=`. Unknown keys are rejected. Inline comments are not supported.

Example for a 10×8 maze:

```text
WIDTH=10
HEIGHT=8
ENTRY=0,0
EXIT=9,7
OUTPUT_FILE=maze.txt
PERFECT=True
```

| Key | Currently accepted meaning |
| --- | --- |
| `WIDTH` | Positive integer: number of columns. |
| `HEIGHT` | Positive integer: number of rows. |
| `ENTRY` | Entry cell as `x,y`, inside the maze. |
| `EXIT` | Exit cell as `x,y`, inside the maze and different from entry. |
| `OUTPUT_FILE` | Required nonempty value; currently unused and no file is written. |
| `PERFECT` | Parser accepts `True` or `False`, ignoring case; generation currently requires `True`. |

Coordinates start at `(0, 0)` in the top-left corner. Increasing `x` moves right;
increasing `y` moves down. Entry and exit are cells, not openings in the outer
border. `SEED` is not an accepted configuration key.

## Maze Representation

Each `Cell` stores its walls in one integer, `walls`. A set bit means that wall
exists:

| Wall | Value | Bit |
| --- | --- | --- |
| `NORTH` | 1 | 0 |
| `EAST` | 2 | 1 |
| `SOUTH` | 4 | 2 |
| `WEST` | 8 | 3 |

Every cell starts with `ALL_WALLS = 15`, combining all four flags. `has_wall()`
checks a wall, `remove_wall()` clears its bit, and `add_wall()` sets it.
This ordering intentionally matches the subject's later hexadecimal wall
encoding: one cell's integer can become one hex digit. Export is not implemented.

The grid is accessed as `generator.maze[y][x]`. Each cell also has a `visited`
flag used during generation.

## Maze Generation Algorithm

The implementation uses randomized DFS / recursive backtracking, written
iteratively with a Python list as a stack rather than recursive function calls.

1. Reset the grid so every cell has all four walls.
2. Start at `(0, 0)`, mark it visited, and put it on the stack.
3. Find its unvisited north/east/south/west neighbours inside the grid.
4. Randomly choose one and remove both sides of the shared wall.
5. Mark that neighbour visited, push it onto the stack, and continue from it.
6. At a dead end, pop the stack to backtrack.
7. Finish when the stack is empty; every cell has been visited.

In `MazeGenerator.generate()`, the paired removal is:

```python
self.maze[y][x].remove_wall(direction)
self.maze[ny][nx].remove_wall(OPPOSITE[direction])
```

For example, moving east removes the current cell's east wall and the next
cell's west wall. Only connecting to unvisited cells prevents loops.

We chose this algorithm because it is simple to explain, fits the cell/grid
representation, and produces a perfect maze. Random neighbour selection gives
variation, while a seed makes the choices repeatable. The explicit stack avoids
Python's recursion-depth limit.

## Seed / Reproducibility

Supply a seed directly to `MazeGenerator` in Python. From the repository root,
this example can be run in a Python interpreter or saved as a script:

```python
from mazegen import MazeGenerator
from display.ascii_renderer import render_ascii

generator = MazeGenerator(
    width=10,
    height=8,
    entry=(0, 0),
    exit_point=(9, 7),
    perfect=True,
    seed=42,
)
generator.generate()
print(render_ascii(generator))
```

Each call to `generate()` resets the grid and creates a local
`random.Random(self.seed)`. With the same implementation and Python environment,
the same dimensions and seed produce the same walls, including on repeated
calls. A different seed may produce a different maze. Entry/exit markers do not
affect generation because the starting cell is fixed.

The command-line program currently leaves the seed as `None`, so its runs are
not reproducible by configuration alone. There is no seed command-line option.

## ASCII Display

The renderer is a minimal development/testing visualization:

- `E`: entry cell.
- `X`: exit cell.
- `---`: horizontal wall; `|`: vertical wall; `+`: wall corner.
- Spaces between cells: open passages.

It reads the generated cells without changing their walls or keeping a second
maze grid. Outer borders stay closed. The renderer can show `EX` if both markers
share a cell through the Python API, although the config parser rejects that
case. There are no interactions, colours, or solution-path controls yet.

## Code Reusability

The maze generator is provided as a reusable python package named `mazegen`.
It can be installed from the generated wheel or the source distribution and
imported into another Python project.

### Creating a generator

The `MazeGenerator` class can be imported and instantiated with custom maze
dimensions, entry and exit positions, generation mode, and an optional seed.

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=10,
    height=8,
    entry=(0, 0),
    exit_point=(9, 7),
    perfect=True,
    seed=42,
)

generator.generate()

After calling generate(), the generated maze is available through generator.maze.

`Cell` represents cell state, and `MazeGenerator` owns the generation logic.
Neither depends on terminal rendering. The ASCII renderer only reads the maze;
the main program connects the parser, generator, and display.

The generator can already be imported from this repository, as shown above.
. Pass `perfect=True` for a perfect maze; the constructor default, `False`, generates
a non-perfect maze.


## Development Progress

Milestone 1 establishes the maze representation, integrates the existing parser,
generates a first perfect maze, and displays it as ASCII. Tests verify seeded
generation and coherent walls, full connectivity, no loops, closed borders,
basic rendering, and invalid generator settings.


## Resources

References consulted while preparing this documentation; these do not imply
that every team member has already studied them:

- [Python tutorial](https://docs.python.org/3/tutorial/): Python fundamentals,
  classes, modules, and data structures.
- [Python random documentation](https://docs.python.org/3/library/random.html):
  local `Random` instances, seeds, and random selection.
- [Jamis Buck: Maze Generation — Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking):
  an explanation and implementation of the backtracking algorithm. Its example
  tracks passages with bits; this project uses set bits for walls instead.

### AI Usage

AI tools assisted with discussing project architecture, breaking the subject
into smaller implementation steps, implementing the first perfect-maze
algorithm, creating basic ASCII visualization, tests, and structuring this
documentation.
