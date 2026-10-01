"""Read configuration, generate maze, displays it and gives output."""

import sys

from display.ascii_renderer import render_ascii
from mazegen import MazeGenerator
from parser import parse_config
from output import generate_output


def main() -> int:
    """Generate and display a maze and create the output file."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    try:
        config = parse_config(sys.argv[1])

        generator = MazeGenerator(
            width=config["WIDTH"],
            height=config["HEIGHT"],
            entry=config["ENTRY"],
            exit_point=config["EXIT"],
            perfect=config["PERFECT"],
        )

        generator.generate()
        path = generator.shortest_path()

        generate_output(
            generator.maze,
            config["OUTPUT_FILE"],
            config["ENTRY"],
            config["EXIT"],
            path,
        )

        show_path = True

        while True:
            print("\033[H\033[J", end="")
            print(render_ascii(generator, path, show_path))

            print()
            print("Commands: [r] Regenerate [p] Show/Hide path  [q] Quit")

            command = input("> ").strip().lower()

            if command == "p":
                show_path = not show_path

            elif command == "r":
                generator.generate()
                path = generator.shortest_path()

                generate_output(
                    generator.maze,
                    config["OUTPUT_FILE"],
                    config["ENTRY"],
                    config["EXIT"],
                    path,
                )

            elif command == "q":
                break

            else:
                print("Unknown command.")

    except KeyError as error:
        # The current parser can access a required key before checking it.
        print(f"Error: Missing required key: {error.args[0]}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError, ValueError, NotImplementedError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
