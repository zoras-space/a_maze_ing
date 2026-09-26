from typing import TypedDict, Union, cast


REQUIRED_KEYS = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]


class Config(TypedDict, total=False):
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool


def convert_value(key: str,
                  value: str) -> Union[int, tuple[int, int], bool, str]:
    if key in ("WIDTH", "HEIGHT"):
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{key} must be an integer")

    if key in ("ENTRY", "EXIT"):
        try:
            x, y = value.split(",")
            return (int(x), int(y))
        except ValueError:
            raise ValueError(f"{key} must use x, y format")

    if key == "PERFECT":
        if value.lower() not in ("true", "false"):
            raise ValueError("PERFECT must be True or False")
        return value.lower() == "true"

    return value


def validate_config(config: Config) -> None:
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"Missing required key: {key}")

        if config["WIDTH"] <= 0:
            raise ValueError("WIDTH must be greater than 0")

        if config["HEIGHT"] <= 0:
            raise ValueError("HEIGHT must be greater than 0")

        entry = config["ENTRY"]
        exit_pos = config["EXIT"]

        if not (0 <= entry[0] < config["WIDTH"] and
                0 <= entry[1] < config["HEIGHT"]):
            raise ValueError("ENTRY is outside the maze")

        if not (0 <= exit_pos[0] < config["WIDTH"] and
                0 <= exit_pos[1] < config["HEIGHT"]):
            raise ValueError("EXIT is outside the maze")

        if entry == exit_pos:
            raise ValueError("ENTRY and EXIT must be different")


def parse_config(filename: str) -> Config:
    with open(filename, "r") as file:
        lines = file.readlines()

    config: dict[str, object] = {}

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ValueError(f"Invalid configurationline: {line}")

        key, value = line.split("=", 1)

        if not key or not value:
            raise ValueError(f"Invalid configurartion line: {line}")

        if key not in REQUIRED_KEYS:
            raise ValueError(f"Unknown configuration key: {key}")

        config[key] = convert_value(key, value)

    typed_config = cast(Config, config)
    validate_config(typed_config)
    return typed_config
