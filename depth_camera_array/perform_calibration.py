import argparse

import numpy as np
import pyrealsense2 as rs
from cv2 import cv2

from depth_camera_array.calibrator import find_qr
# from depth_camera_array.camera import initialize_connected_cameras
from depth_camera_array.camera import initialize_connected_cameras


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes an extrinsic calibration for all available cameras')
    parser.add_argument('--output', type=str, required=True, help='Path to output file')
    return parser.parse_args()


def dump_scene():
    base_path = '/home/matze/projects/depth_camera_array/data'
    try:
        cameras = initialize_connected_cameras()
        for camera in cameras:
            for k, v in camera.poll_frames().items():
                v.dump(f'{base_path}/{camera._device_id}_{k}')
                if k == 'color':
                    cv2.imwrite(f'{base_path}/{camera._device_id}_color.png', v)

    except RuntimeError as error:
        print(error)
    finally:
        camera.close()





def check_single_rgb():
    pipeline = rs.pipeline()
    pipeline.start()

    # Create a pipeline object. This object configures the streaming camera and owns it's handle
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())
    # rgb = np.random.randint(255, size=(900, 800, 3), dtype=np.uint8)
    cv2.imwrite('/home/matze/projects/depth_camera_array/data/single.png', color_image)
    pipeline.stop()


def main():
    """Creates a camera setup file containing camera ids and extrinsic information"""
    # args = parse_args()
    # cameras = initialize_connected_cameras()
    # print(len(cameras))
    # cameras[0].poll_frames()
    # check_single_rgb()
    dump_scene()
    # find_qr('/home/matze/projects/depth_camera_array/data/single.png')

    # 1. Identify cameras
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
