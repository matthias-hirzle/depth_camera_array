import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes an extrinsic calibration for all available cameras')
    parser.add_argument('--output', type=str, required=True, help='Path to output file')
    return parser.parse_args()


def main():
    """Creates a camera setup file containing camera ids and extrinsic information"""
    args = parse_args()


if __name__ == '__main__':
    main()
