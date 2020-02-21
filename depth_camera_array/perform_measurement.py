import argparse
import math
import multiprocessing as mp
import os
from typing import Any, Tuple

import numpy as np
from open3d import open3d as o3d

from depth_camera_array.camera import Camera, initialize_connected_cameras
from depth_camera_array.utilities import load_json_to_dict, get_or_create_data_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Measures the scene')
    parser.add_argument('--camera_setup', type=str, help='Path to the file, created by calibration module')
    parser.add_argument('--bottom', type=float, default=0.0, help='Bottom of the measurement sphere in m')
    parser.add_argument('--height', type=float, default=1.8, help='Height of the measurement sphere in m')
    parser.add_argument('--radius', type=float, default=0.5, help='Radius of the measurement sphere in m')
    parser.add_argument('--data_dir', type=str, help='Data location to load and dump config files',
                        default=get_or_create_data_dir())
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


def remove_unnecessary_content(object_points, bottom: float, height: float, radius: float) -> np.array:
    """Removes points that are not in range"""
    filtered_points = []
    for item in object_points:
        if is_in_range(item, bottom, height, radius):
            filtered_points.append(item.tolist())
    return filtered_points


def transform(object_points: list, extrinsics: np.array):
    temp = np.array(object_points).transpose()
    points = np.ones((4, temp.shape[1],))
    points[:-1, :] = temp
    transformed = extrinsics.dot(points)
    return transformed[:-1, :].transpose()


def dump_to_ply(object_points: np.array, data_dir: str, camera_id: str):
    points = np.array(object_points)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    o3d.io.write_point_cloud(os.path.join(data_dir, f'{camera_id}.ply'), pcd)


def measure_per_camera(camera: Camera, extrinsic: np.array, bottom, height, radius) -> Tuple[str, list]:
    frames = camera.poll_frames()
    object_points = camera.depth_frame_to_object_point(frames)
    object_points = transform(object_points, np.array(extrinsic))
    object_points = remove_unnecessary_content(object_points, bottom, height, radius)
    return camera.device_id, object_points


def main():
    args = parse_args()
    transformations = load_json_to_dict(os.path.join(args.data_dir, 'camera_array.json'))
    connected_cameras = initialize_connected_cameras()
    with mp.Pool(mp.cpu_count()) as pool:
        procs = [
            pool.apply_async(
                measure_per_camera,
                (camera, transformations[camera.device_id], args.bottom, args.height, args.radius)
            )
            for camera in connected_cameras
        ]
        results = [proc.get() for proc in procs]
    # wait until pool is closed
    pool.join()
    for result in results:
        dump_to_ply(result[1], args.data_dir, result[0])


if __name__ == '__main__':
    main()
