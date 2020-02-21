import argparse
import math
import os
from typing import Any

from depth_camera_array import camera
from depth_camera_array.utilities import load_json_to_dict, get_or_create_data_dir, dump_dict_as_json
import pyrealsense2 as rs

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Measures the scene')
    parser.add_argument('--camera_setup', type=str, help='Path to the file, created by calibration module')
    parser.add_argument('--bottom', type=float, default=0.0, help='Bottom of the measurement sphere in m')
    parser.add_argument('--height', type=float, default=1.8, help='Height of the measurement sphere in m')
    parser.add_argument('--radius', type=float, default=0.5, help='Radius of the measurement sphere in m')
    parser.add_argument('--data_dir', type=str, help='Data location to load and dump config files', default=get_or_create_data_dir())
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


def remove_unnecessary_content(object_points, bottom: float, height: float, radius: float) -> Any:
    """Removes points that are not in range"""
    return np.array(list(filter(lambda item: is_in_range(item, bottom, height, radius), object_points)))


def transform(object_points:list, extrinsics:np.array):
    temp = np.array(object_points).transpose()
    points = np.ones((4, temp.shape[1],))
    points[:-1, :] = temp
    transformed = extrinsics.dot(points)
    return transformed[:-1,:].transpose()

def dump_to_ply(merged_point_cloud):
    pass


def main():
    args = parse_args()
    dictionary = load_json_to_dict(os.path.join(args.data_dir, 'camera_array.json'))
    all_connected_cams = camera.initialize_connected_cameras()
    for cam in all_connected_cams:
        trans_matrix = np.array(dictionary[cam.device_id])
        frames = cam.poll_frames()
        object_points = cam.depth_frame_to_object_point(frames)
        object_points = transform(object_points, np.array(trans_matrix))
        object_points = remove_unnecessary_content(object_points, args.bottom, args.height, args.radius)
        dump_dict_as_json({cam.device_id:object_points.tolist()})
    # merge point clouds
    merged_point_cloud = None
    #dump_to_ply(merged_point_cloud, args.data_dir)  # TODO move to Util


if __name__ == '__main__':
    main()
