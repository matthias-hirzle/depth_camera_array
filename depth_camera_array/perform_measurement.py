import argparse
import os

import numpy as np
from open3d import open3d as o3d

from depth_camera_array import camera
from depth_camera_array.utilities import load_json_to_dict, create_if_not_exists, dump_dict_as_json, DEFAULT_DATA_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Measures the scene')
    parser.add_argument('--bottom', type=float, default=0.0, help='Bottom of the measurement sphere in m')
    parser.add_argument('--height', type=float, default=1.8, help='Height of the measurement sphere in m')
    parser.add_argument('--radius', type=float, default=0.5, help='Radius of the measurement sphere in m')
    parser.add_argument('--data_dir', type=lambda item: create_if_not_exists(item), default=DEFAULT_DATA_DIR,
                        help='Data location to load and dump config files', )
    return parser.parse_args()


def is_in_measurement_cylinder(point: np.array, bottom: float, height: float, radius: float) -> bool:
    is_beside_cylinder = np.linalg.norm([point[0], point[2]]) > radius
    is_above_cylinder = point[1] > (bottom + height)
    is_below_cylinder = point[1] < bottom
    return not (is_beside_cylinder or is_above_cylinder or is_below_cylinder)


def remove_unnecessary_content(object_points, bottom: float, height: float, radius: float) -> np.array:
    """Removes points outside the defined measurement cylinder"""
    filtered_points = []
    for item in object_points:
        if is_in_measurement_cylinder(item, bottom, height, radius):
            filtered_points.append(item.tolist())
    return filtered_points


def apply_transformation(object_points: np.array, extrinsic: np.array) -> np.array:
    tmp = object_points.transpose()
    points = np.ones((4, tmp.shape[1],))
    points[:-1, :] = tmp
    transformed = extrinsic.dot(points)
    return transformed[:-1, :].transpose()


def dump_to_ply(object_points: np.array, data_dir: str, camera_id: str):
    points = np.array(object_points)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    o3d.io.write_point_cloud(os.path.join(data_dir, f'{camera_id}.ply'), pcd)


def main():
    args = parse_args()
    dictionary = load_json_to_dict(os.path.join(args.data_dir, 'camera_array.json'))
    all_connected_cams = camera.initialize_connected_cameras()
    for cam in all_connected_cams:
        trans_matrix = np.array(dictionary[cam.device_id])
        frames = cam.poll_frames()
        object_points = cam.depth_frame_to_object_points(frames)
        object_points = apply_transformation(object_points, np.array(trans_matrix))
        object_points = remove_unnecessary_content(object_points, args.bottom, args.height, args.radius)
        serial_points = np.array(object_points).transpose()
        dump_dict_as_json({cam.device_id: serial_points.tolist()},
                          os.path.join(args.data_dir, cam.device_id + '_object_points.json'))
        dump_to_ply(object_points, args.data_dir, cam.device_id)


if __name__ == '__main__':
    main()
