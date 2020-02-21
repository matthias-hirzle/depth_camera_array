import argparse
import os

from depth_camera_array.utilities import get_or_create_data_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Detects all available acuro markers')
    parser.add_argument('--data_dir', type=str, required=False, help='Data location to load and dump config files',
                        default=get_or_create_data_dir())
    return parser.parse_args()


args = parse_args()
directory = args.data_dir
if os.path.exists(directory):
    for file in os.listdir(directory):
        if file.endswith(".json"):
            # print(directory + '/' + file)
            os.remove(directory + '/' + file)