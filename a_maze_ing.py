import sys

from parser import parse_config


def main():
    if len(sys.argv) != 2:
        raise ValueError("Usage: python3 a_maze_ing.py config.txt")

    try:
        config = parse_config(sys.argv[1])
    except FileNotFoundError:
        raise ValueError(f"Configuration file not found: {sys.argv[1]}")

    print(config)


if __name__ == "__main__":
    main()
