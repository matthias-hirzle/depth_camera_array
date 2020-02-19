import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Measures the scene')
    parser.add_argument('--camera_setup', type=str, help='Path to the file, created by calibration module')
    parser.add_argument('--bottom', type=int, help='Bottom of the measurement sphere in mm')
    parser.add_argument('--height', type=int, help='Height of the measurement sphere in mm')
    parser.add_argument('--radius', type=int, help='Radius of the measurement sphere in mm')
    parser.add_argument('--data_dir', type=str, help='Data location to load and dump config files')
    return parser.parse_args()


def main():
    args = parse_args()


if __name__ == '__main__':
    main()
