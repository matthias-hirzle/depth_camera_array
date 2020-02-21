import argparse
import math
import os
from typing import Any

from depth_camera_array import camera


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Measures the scene')
    parser.add_argument('--camera_setup', type=str, help='Path to the file, created by calibration module')
    parser.add_argument('--bottom', type=int, help='Bottom of the measurement sphere in mm')
    parser.add_argument('--height', type=int, help='Height of the measurement sphere in mm')
    parser.add_argument('--radius', type=int, help='Radius of the measurement sphere in mm')
    parser.add_argument('--data_dir', type=str, help='Data location to load and dump config files')
    return parser.parse_args()


def is_in_range(point: Any, bottom: float, height: float, radius: float) -> bool:
    # √x2 + z2 <= r
    a = math.sqrt(math.pow(point[0], 2) + math.pow(point[2], 2)) <= radius
    # y < b + h
    b = point[1] < bottom + height
    # y > b
    c = height > bottom

    if a and b and c:
        return True
    else:
        return False


def remove_unnecessary_content(point_cloud: Any, bottom: float, height: float, radius: float) -> Any:
    """Removes points that are not in range"""
    return filter(lambda item: is_in_range(item, bottom, height, radius), point_cloud)


def transform(device_id: str, point_cloud: Any, data_dir: str):
    pass


def dump_to_ply(merged_point_cloud):
    pass


def main():
    args = parse_args()
    all_connected_cams = camera.initialize_connected_cameras()
    for cam in all_connected_cams:
        frames = cam.poll_frames()
        point_cloud = cam.get_point_cloud(frames)
        point_cloud.export_to_ply(os.path.join("C:\AutoSysLab\depth_camera_array\data", 'gedoens.ply'), frames.get_color_frame())

        #transform(cam.device_id, point_cloud, args.data_dir)
        #remove_unnecessary_content(point_cloud, args.bottom, args.height, args.radius)
    # merge point clouds
    merged_point_cloud = None
    #dump_to_ply(merged_point_cloud, args.data_dir)  # TODO move to Util


if __name__ == '__main__':
    main()
