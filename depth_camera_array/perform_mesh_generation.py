import argparse

from depth_camera_array.utilities import DEFAULT_DATA_DIR, create_if_not_exists


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes a mesh generation to the given coordinates')
    parser.add_argument('--data_dir', type=lambda item: create_if_not_exists(item), default=DEFAULT_DATA_DIR,
                        help='Data location to load and dump config files')
    return parser.parse_args()


def main():
    args = parse_args()


if __name__ == '__main__':
    main()
