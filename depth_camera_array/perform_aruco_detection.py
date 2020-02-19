import argparse
import os

from cv2 import aruco
import json

from depth_camera_array.camera import initialize_connected_cameras, extract_color_image, image_points_to_object_points
from typing import List, Tuple

from depth_camera_array.utilities import get_or_create_data_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Detects all available acuro markers')
    parser.add_argument('--base_path', type=str, required=False, help='Path to output file',
                        default=get_or_create_data_path())
    return parser.parse_args()


def main():
    args = parse_args()
    cameras = initialize_connected_cameras()
    for cam in cameras:
        frames = cam.poll_frames()
        all_2d_centers_of_arucos, all_detected_aruco_ids = read_aruco_codes_from_frame(frames)
        tree_dimensional_points = image_points_to_object_points(all_2d_centers_of_arucos, frames)
        assert len(tree_dimensional_points) == len(all_detected_aruco_ids)
        dump_arcuro_data(cam._device_id, all_detected_aruco_ids, tree_dimensional_points, args.base_path)


def read_aruco_codes_from_frame(frames):
    rgb_image = extract_color_image(frames)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
    detected_coords, ids, _ = aruco.detectMarkers(rgb_image, aruco_dict)
    all_2d_centers = []
    for index, cam_id in enumerate(ids):  # for each found aruco-code
        act_coord = detected_coords[index]
        center_of_actual_code = calc_center_coordinates(act_coord)
        all_2d_centers.append(center_of_actual_code)
    return all_2d_centers, ids.tolist()


def calc_center_coordinates(corners) -> List[float]:
    coordinates = corners[0]
    x_sum = 0
    y_sum = 0
    assert len(coordinates) == 4  # should find four corner coordinates
    for coord in coordinates:
        x_sum += coord[0]
        y_sum += coord[1]
    return [x_sum / 4, y_sum / 4]

# write data to json file
def dump_arcuro_data(camera_id: str, code_id_array: List[str], coordinate_array: List[Tuple[float, float, float]], base_path: str):

    new_dict = {}
    new_dict.update(camera_id=camera_id)
    new_dict.update(aruco=code_id_array)
    new_dict.update(centers=coordinate_array)

    # write to a file
    with open(os.path.join(base_path, f'{camera_id}_reference_points.json'), 'w')as json_file:
        json.dump(new_dict, json_file)


if __name__ == '__main__':
    main()
