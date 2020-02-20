import argparse
import os

import rmsd

from depth_camera_array.utilities import get_or_create_data_dir, load_json_to_dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes an extrinsic calibration for all available cameras')
    parser.add_argument('--data_dir', type=str, required=False, help='Data location to load and dump config files', default=get_or_create_data_dir())
    return parser.parse_args()


# read data from multiple files
def read_aruco_data(data_dir: str):
    calibration_data = {}
    for file in os.listdir(data_dir):
        if file.endswith("_reference_points.json"):
            reference_points = load_json_to_dict(file)
            calibration_data['camera_id'] = {
                {
                    'aruco': calibration_data['aruco'],
                    'centers': calibration_data['centers']
                }
            }
    return calibration_data


def calculate_transformation_kabsch(src_points, dst_points):
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

    return rotation_matrix.transpose(), translation_vector.transpose(), rmsd_value


def main():
    """Creates a camera setup file containing camera ids and extrinsic information"""
    args = parse_args()
    # 1. read aruco data

    # 2. Take frames rgb and depth for each camera
    # 3. qr detection through calibrator
    # 4. intersection of detected points through qr id
    # 5. generate extrinsics
    # 6. take frames from bottom
    # 7. determine direction of z-axis
    # 8. adjust all extrinsics
    # 9. dump extrinsics and device ids for next step.


if __name__ == '__main__':
    main()
