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
        wall_colours = ["white", "blue", "green", "red", "cyan"]
        wall_colour_index = 0

        while True:
            print("\033[H\033[J", end="")
            print(
                render_ascii(
                    generator,
                    path,
                    show_path,
                    wall_colours[wall_colour_index],
                )
            )

            print()
            print("1. Re-generate maze")
            print("2. Show/Hide shortest path")
            print("3. Change wall colours")
            print("4. Quit")

            command = input("Choice (1-4): ").strip()

            if command == "2":
                show_path = not show_path

            elif command == "3":
                wall_colour_index = (
                    wall_colour_index + 1
                ) % len(wall_colours)

            elif command == "1":
                generator.generate()
                path = generator.shortest_path()

                generate_output(
                    generator.maze,
                    config["OUTPUT_FILE"],
                    config["ENTRY"],
                    config["EXIT"],
                    path,
                )

            elif command == "4":
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
