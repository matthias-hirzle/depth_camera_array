import argparse

# from depth_camera_array.camera import initialize_connected_cameras
from depth_camera_array.utilities import get_or_create_data_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Detects all available acuro markers')
    parser.add_argument('--base_path', type=str, required=False, help='Path to output file',
                        default=get_or_create_data_path())
    return parser.parse_args()


def main():
    args = parse_args()


if __name__ == '__main__':
    main()
