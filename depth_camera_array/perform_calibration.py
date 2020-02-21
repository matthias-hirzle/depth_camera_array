import argparse
import os
from typing import Tuple, Dict

import numpy as np
import rmsd

from depth_camera_array.depth_camera_array.utilities import get_or_create_data_dir, load_json_to_dict, dump_dict_as_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes an extrinsic calibration for each available camera')
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


def calculate_absolute_transformations(relative_transformations: Dict[str, np.array], aruco_data: dict,
                                       base_camera: str) -> Dict[str, np.array]:
    # find bottom markers
    markers = aruco_data[base_camera]['aruco']
    points = aruco_data[base_camera]['centers']
    bottom_points = []
    marker_points = []
    for item in zip(markers, points):
        if item[0] < 20:
            bottom_points.append(item[1])
        else:
            marker_points.append(item[1])
    assert len(bottom_points) > 2

    # estimate destination direction
    reference_point = np.array(marker_points[0])
    edge_points = np.array(list(map(lambda item: np.array(item), bottom_points[:3])))

    # 1. normale
    norm = np.cross(edge_points[0] - edge_points[1], edge_points[0] - edge_points[2])
    if np.linalg.norm(reference_point - norm) > np.linalg.norm(reference_point + norm):
        norm = norm * (-1)

    src_center = edge_points[0]
    src_x = edge_points[1]
    src_y = src_center + norm

    dst_center = np.array([0., 0., 0.])
    dst_x = np.array([np.linalg.norm(src_center - src_x), 0., 0.])
    dst_y = np.array([0., abs(np.linalg.norm(norm)), 0.])

    src_points = np.array([src_x, src_y, src_center])
    dst_points = np.array([dst_x, dst_y, dst_center])
    transformation, rmsd_value = calculate_transformation_kabsch(src_points.transpose(), dst_points.transpose())
    print("RMS error for calibration to real world system is :", rmsd_value, "m")

    final_transformations = {}
    for k, v in relative_transformations.items():
        final_transformations[k] = np.dot(transformation, v)
    return final_transformations


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

    p1 = np.array([1, 0, 0])
    p2 = np.array([0, 0, 0])
    p3 = np.array([0, 1, 0])
    p4 = np.array([0, 0, 1])
    src = np.array([p1, p1, p2, p3]).transpose()
    dst = np.array([p1, p1, p2, p4]).transpose()
    mat, err = calculate_transformation_kabsch(src, dst)

    homop = np.ones(4)
    homop[:3] = p3
    p5 = mat.dot(homop)

    pass


if __name__ == '__main__':
    main()
