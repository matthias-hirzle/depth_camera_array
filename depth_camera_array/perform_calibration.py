import argparse
import json
import os

from depth_camera_array.utilities import get_or_create_data_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes an extrinsic calibration for all available cameras')
    parser.add_argument('--data_dir', type=str, required=False, help='Data location to load and dump config files', default=get_or_create_data_dir())
    return parser.parse_args()


# read data from multiple files
def read_aruco_data():
    data = []
    directory = ""

    for filename in os.listdir(directory):
        if filename.endswith("_reference_points.json"):
            f = open(filename)
            data.append(json.loads(f.read()))


def main():
    """Creates a camera setup file containing camera ids and extrinsic information"""
    args = parse_args()
    # 1. Identify cameras
    # 2. Take frames rgb and depth for each camera
    # 3. qr detection through calibrator
    # 4. intersection of detected points through qr id
    # 5. generate extrinsics
    # 6. take frames from bottom
    # 7. determine direction of z-axis
    # 8. adjust all extrinsics
    # 9. dump extrinsics and device ids for next step.


if __name__ == '__main__':
    main()
