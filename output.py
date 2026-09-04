def write_output(filename: str, content: str) -> None:
    with open(filename, "w") as file:
        file.write(content)
