import argparse
import os
from typing import Tuple, Dict

import numpy as np
import rmsd

from depth_camera_array.utilities import get_or_create_data_dir, load_json_to_dict, dump_dict_as_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes an extrinsic calibration for all available cameras')
    parser.add_argument('--data_dir', type=str, required=False, help='Data location to load and dump config files',
                        default=get_or_create_data_dir())
    return parser.parse_args()


# read data from multiple files
def read_aruco_data(data_dir: str):
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
    src_points = src_points.transpose()
    dst_points = dst_points.transpose()
    assert src_points.shape == dst_points.shape
    print(src_points.shape)
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


def define_base_camera(aruco_data: dict) -> str:
    base_camera = None
    arucos = 0
    bottom_arucos = set(range(20))
    for k, v in aruco_data.items():
        intersected = len(bottom_arucos.intersection(set(v['aruco'])))
        if intersected > arucos:
            arucos = intersected
            base_camera = k
    assert arucos > 2
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
    source_arucos = aruco_data[base_camera]['aruco']
    source_points = aruco_data[base_camera]['centers']
    for k, v in aruco_data.items():
        if not k == base_camera:
            # 1. intersect arucos
            dest_arucos = v['aruco']
            dest_points = v['centers']
            intersection = set(source_arucos).intersection(set(dest_arucos))
            # 2. create two sorted lists of points
            assert len(intersection) > 2
            source_sorted = []
            dest_sorted = []
            for aruco_id in intersection:
                source_sorted.append(source_points[source_arucos.index(aruco_id)])
                dest_sorted.append(dest_points[dest_arucos.index(aruco_id)])

            transformation, rmsd_value = calculate_transformation_kabsch(np.array(source_sorted), np.array(dest_sorted))
            print("RMS error for calibration with device number", k, "is :", rmsd_value, "m")
            transformations[k] = transformation

    return transformations


def calculate_absolute_transformations(relative_transformations: Dict[str, np.array], aruco_data: dict,
                                       base_camera: str) -> Dict[str, np.array]:
    # find bottom markers

    # create l2 norm

    # check direction of l2 norm

    #
    return relative_transformations


def generate_extrinsics(aruco_data: dict) -> dict:
    # 1. define base_camera
    base_camera = define_base_camera(aruco_data)
    relative_transformations = calculate_relative_transformations(aruco_data, base_camera)
    final_transformations = calculate_absolute_transformations(relative_transformations, aruco_data, base_camera)
    for k, v in final_transformations.items():
        final_transformations[k] = v.tolist()
    return final_transformations


def main():
    """Creates a camera setup file containing camera ids and extrinsic information"""
    args = parse_args()
    aruco_data = read_aruco_data(args.data_dir)
    transformations = generate_extrinsics(aruco_data)
    dump_dict_as_json(transformations, os.path.join(args.data_dir, 'camera_array.json'))
    print(os.path.realpath(__file__))


if __name__ == '__main__':
    main()
