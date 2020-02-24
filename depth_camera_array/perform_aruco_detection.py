import argparse
import os
from typing import List, Tuple

import numpy as np
import rmsd
from cv2 import aruco

from depth_camera_array.camera import initialize_connected_cameras, extract_color_image, close_connected_cameras
from depth_camera_array.utilities import create_if_not_exists, dump_dict_as_json, DEFAULT_DATA_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Detects all available acuro markers')
    parser.add_argument('--data_dir', type=lambda item: create_if_not_exists(item), required=False,
                        help='Data location to load and dump config files', default=DEFAULT_DATA_DIR)
    parser.add_argument('--remove_previous_data', action='store_true',
                        help='If set, each reference-point file in data_dir will be removed before performing new '
                             'detection.')
    return parser.parse_args()


def remove_previous_data(data_dir: str):
    for file in os.listdir(data_dir):
        if file.endswith('_reference_points.json'):
            os.remove(os.path.join(data_dir, file))


def main():
    args = parse_args()
    if args.remove_previous_data:
        remove_previous_data(args.data_dir)

    cameras = initialize_connected_cameras()
    for camera in cameras:
        frames = camera.poll_frames()
        color_frame = extract_color_image(frames)

        aruco_corners_image_points, aruco_ids = detect_aruco_targets(color_frame)
        aruco_centers_image_points = [determine_aruco_center(corners) for corners in aruco_corners_image_points]
        aruco_centers_object_points = camera.image_points_to_object_points(aruco_centers_image_points, frames)

        dump_reference_points(camera.device_id, aruco_ids, aruco_centers_object_points, args.data_dir)
    close_connected_cameras(cameras)


def detect_aruco_targets(rgb_image: np.array) -> Tuple[np.array, List[int]]:
    aruco_corners, aruco_ids, _ = aruco.detectMarkers(rgb_image, aruco.Dictionary_get(aruco.DICT_5X5_250))
    return np.array([item[0] for item in aruco_corners]), [item[0] for item in aruco_ids]


def determine_aruco_center(corners: np.array) -> np.array:
    assert corners.shape == (4, 2,)
    return rmsd.centroid(corners)


def dump_reference_points(device_id: str, aruco_ids: List[int], aruco_centers: List[np.array], data_dir: str):
    reference_points = {
        'camera_id': device_id,
        'aruco': aruco_ids,
        'centers': aruco_centers
    }
    dump_dict_as_json(reference_points, os.path.join(data_dir, f'{device_id}_reference_points.json'))


if __name__ == '__main__':
    main()
