import argparse
from depth_camera_array import camera
from cv2 import cv2
from cv2 import aruco

# from depth_camera_array.camera import initialize_connected_cameras
from typing import List, Tuple

from depth_camera_array.utilities import get_or_create_data_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Detects all available acuro markers')
    parser.add_argument('--base_path', type=str, required=False, help='Path to output file',
                        default=get_or_create_data_path())
    return parser.parse_args()


def main():
    # args = parse_args()
    cameras = camera.initialize_connected_cameras()
    # rgb_image = cv2.imread("817612070307_color.png") #for testing reasons without having a cam connected
    for cam in cameras:
        frames = cam.poll_frames()
        rgb_image = cam.extract_color_image(frames)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
        detected_coords, ids, _ = aruco.detectMarkers(rgb_image, aruco_dict)
        all_3d_points = []
        for index, cam_id in enumerate(ids):  # for each found aruco-code
            act_coord = detected_coords[index]
            centers = calc_center_coordinates(act_coord)
            tree_dimensional_points = cam.image_points_to_object_points(centers, frames)
            all_3d_points.append(tree_dimensional_points)
            print(centers)
        assert len(all_3d_points) == len(ids)
        dump_arcuro_data(cam._device_id, ids, all_3d_points)

def calc_center_coordinates(corners) -> Tuple[int, int]:
    coordinates = corners[0]
    x_sum = 0
    y_sum = 0
    assert len(coordinates) == 4  # should find four corner coordinates
    for coord in coordinates:
        x_sum += coord[0]
        y_sum += coord[1]
    return [x_sum / 4, y_sum / 4]

def dump_arcuro_data(camera_id: str, code_id_array: List[str], coordinate_array: List[Tuple[int, int, int]]):
    pass


if __name__ == '__main__':
    main()
