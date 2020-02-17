import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cameras', action=list)  # TODO: information to identify cameras and catch them
    parser.add_argument('--output', help='Path to output file')
    return parser.parse_args()


def main():
    """Creates a camera setup file containing camera ids and extrinsics"""
    args = parse_args()


if __name__ == '__main__':
    main()
