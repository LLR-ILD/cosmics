import argparse
from pathlib import Path

example_path = Path(__file__).parents[2] / "example/cosmics.yaml"
print(example_path)
assert example_path.is_file()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path, help=f"See {example_path} as an example.")


if __name__ == "__main__":
    main()
