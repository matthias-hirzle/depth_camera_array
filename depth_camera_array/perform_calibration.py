import argparse
import os
from typing import Tuple, Dict, Iterable, List, Union

import numpy as np
import rmsd

from depth_camera_array.utilities import create_if_not_exists, load_json_to_dict, dump_dict_as_json, DEFAULT_DATA_DIR

ReferencePoints = Dict[str, Dict[str, List[Union[int, Tuple[float, float, float]]]]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes an extrinsic calibration for each available camera')
    parser.add_argument('--data_dir', type=lambda item: create_if_not_exists(item), default=DEFAULT_DATA_DIR,
                        help='Data location to load and dump config files')
    return parser.parse_args()


def read_aruco_data(data_dir: str) -> dict:
    calibration_data = {}
    for file in os.listdir(data_dir):
        if file.endswith("_reference_points.json"):
            reference_points = load_json_to_dict(os.path.join(data_dir, file))
            calibration_data[reference_points['camera_id']] = {
                'aruco': reference_points['aruco'],
                'centers': reference_points['centers']
            }
    return calibration_data


def calculate_transformation_kabsch(src_points: np.ndarray, dst_points: np.ndarray) -> Tuple[np.array, float]:
    """
    Calculates the optimal rigid transformation from src_points to
    dst_points
    (regarding the least squares error)
    Parameters:
    -----------
    src_points: array
        (3,N) matrix
    dst_points: array
        (3,N) matrix

    Returns:
    -----------
    rotation_matrix: array
        (3,3) matrix

    translation_vector: array
        (3,1) matrix
    rmsd_value: float
    """
    assert src_points.shape == dst_points.shape
    if src_points.shape[0] != 3:
        raise Exception("The input data matrix had to be transposed in order to compute transformation.")

    src_points = src_points.transpose()
    dst_points = dst_points.transpose()

    src_points_centered = src_points - rmsd.centroid(src_points)
    dst_points_centered = dst_points - rmsd.centroid(dst_points)

    rotation_matrix = rmsd.kabsch(src_points_centered, dst_points_centered)
    rmsd_value = rmsd.kabsch_rmsd(src_points_centered, dst_points_centered)

    translation_vector = rmsd.centroid(dst_points) - np.matmul(rmsd.centroid(src_points), rotation_matrix)

    return create_homogenous(rotation_matrix.transpose(), translation_vector.transpose()), rmsd_value


def create_homogenous(rotation_matrix: np.array, translation_vector: np.array) -> np.array:
    homogenous = np.append(rotation_matrix, [[vec] for vec in translation_vector], axis=1)
    homogenous = np.append(homogenous, np.array([[0, 0, 0, 1]]), axis=0)
    return homogenous


def define_base_camera(aruco_data: ReferencePoints) -> str:
    """Finds the camera that detected each bottom target and also detected the highest amount of other targets"""
    base_camera = None
    detected_targets = 0
    bottom_arucos = {1, 2, 3}
    for k, v in aruco_data.items():
        if bottom_arucos <= set(v['aruco']) and len(v['aruco']) > detected_targets:
            base_camera = k
            detected_targets = len(v['aruco'])

    assert base_camera is not None
    return base_camera


def calculate_relative_transformations(aruco_data: dict, base_camera: str) -> Dict[str, np.array]:
    transformations = {
        base_camera: np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 1]],
            dtype=float)
    }
    dst_arucos = aruco_data[base_camera]['aruco']
    dst_points = aruco_data[base_camera]['centers']
    for k, v in aruco_data.items():
        if not k == base_camera:
            # 1. intersect arucos
            src_arucos = v['aruco']
            src_points = v['centers']
            intersection = set(dst_arucos).intersection(set(src_arucos))
            # 2. create two sorted lists of points
            assert len(intersection) > 2
            dst_sorted = []
            src_sorted = []
            for aruco_id in intersection:
                dst_sorted.append(dst_points[dst_arucos.index(aruco_id)])
                src_sorted.append(src_points[src_arucos.index(aruco_id)])

            transformation, rmsd_value = calculate_transformation_kabsch(np.array(src_sorted).transpose(),
                                                                         np.array(dst_sorted).transpose())
            print("RMS error for calibration with device number", k, "is :", rmsd_value, "m")
            transformations[k] = transformation

    return transformations


def calculate_absolute_transformations(reference_points: Iterable[Tuple[int, Tuple[float, float, float]]]) -> np.array:
    # find bottom markers
    src_x, src_center, src_z = None, None, None
    for marker_id, point in reference_points:
        if marker_id == 1:
            src_x = np.array(point)
        elif marker_id == 2:
            src_center = np.array(point)
        elif marker_id == 3:
            src_z = np.array(point)

    assert not (src_x is None or src_center is None or src_z is None)

    dst_center = np.array([0., 0., 0.])
    dst_x = np.array([np.linalg.norm(src_center - src_x), 0., 0.])
    dst_z = np.array([0., 0., np.linalg.norm(src_center - src_z)])

    src_points = np.array([src_x, src_z, src_center])
    dst_points = np.array([dst_x, dst_z, dst_center])
    transformation, rmsd_value = calculate_transformation_kabsch(src_points.transpose(), dst_points.transpose())
    print("RMS error for calibration to real world system is :", rmsd_value, "m")

    return transformation


def generate_extrinsics(aruco_data: dict) -> dict:
    base_camera = define_base_camera(aruco_data)
    base_camera_reference_points = zip(aruco_data[base_camera]['aruco'], aruco_data[base_camera]['centers'])
    relative_transformations = calculate_relative_transformations(aruco_data, base_camera)
    absolute_transformation = calculate_absolute_transformations(base_camera_reference_points)
    final_transformations = {}
    for k, v in relative_transformations.items():
        final_transformations[k] = np.dot(absolute_transformation, v)
    # final_transformations = calculate_absolute_transformations(relative_transformations, aruco_data, base_camera)

    return final_transformations


def main():
    """Creates a camera setup file containing camera ids and extrinsic information as 4 x 4 matrix"""
    args = parse_args()
    aruco_data = read_aruco_data(args.data_dir)
    final_transformations = generate_extrinsics(aruco_data)
    for k, v in final_transformations.items():
        final_transformations[k] = v.tolist()
    dump_dict_as_json(final_transformations, os.path.join(args.data_dir, 'camera_array.json'))


if __name__ == '__main__':
    main()
