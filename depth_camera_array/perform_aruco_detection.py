import argparse
import os
from typing import List, Tuple

import numpy as np
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


def main():
    args = parse_args()
    if args.remove_previous_data:
        for file in os.listdir(args.data_dir):
            if file.endswith('_reference_points.json'):
                os.remove(os.path.join(args.data_dir, file))

    cameras = initialize_connected_cameras()
    for cam in cameras:
        frames = cam.poll_frames()

        color_frame = extract_color_image(frames)

        all_2d_centers_of_arucos, all_detected_aruco_ids = detect_aruco_targets(frames)
        tree_dimensional_points = cam.image_points_to_object_points(all_2d_centers_of_arucos, frames)
        assert len(tree_dimensional_points) == len(all_detected_aruco_ids)
        dump_arcuro_data(cam.device_id, all_detected_aruco_ids, tree_dimensional_points, args.data_dir)
    close_connected_cameras(cameras)


def detect_aruco_targets(rgb_image: np.array):
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
    detected_coords, ids, _ = aruco.detectMarkers(rgb_image, aruco_dict)
    print('< camera id | detected codes >')
    print(ids)
    all_2d_centers = []
    if ids is not None:
        for index, cam_id in enumerate(ids):  # for each found aruco-code
            act_coord = detected_coords[index]
            center_of_actual_code = calc_center_coordinates(act_coord)
            all_2d_centers.append(center_of_actual_code)
        ids = [int(id[0]) for id in ids]
    else:
        print('NO Codes detected for actual Camera!!!')
        ids = []  # return an empty list instead of none
    return all_2d_centers, ids


def calc_center_coordinates(corners) -> List[float]:
    coordinates = corners[0]
    x_sum = 0
    y_sum = 0
    assert len(coordinates) == 4  # should find four corner coordinates
    for coord in coordinates:
        x_sum += coord[0]
        y_sum += coord[1]
    return [x_sum / 4, y_sum / 4]


def dump_arcuro_data(camera_id: str, code_id_array: List[str], coordinate_array: List[Tuple[float, float, float]],
                     data_dir: str):
    new_dict = {}
    new_dict.update(camera_id=camera_id)
    new_dict.update(aruco=code_id_array)
    new_dict.update(centers=coordinate_array)

    # write to a file
    dump_dict_as_json(new_dict, os.path.join(data_dir, f'{camera_id}_reference_points.json'))


if __name__ == '__main__':
    main()
