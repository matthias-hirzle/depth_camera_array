import argparse
import pyrealsense2 as rs
from depth_camera_array.camera import initialize_connected_cameras


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Performes an extrinsic calibration for all available cameras')
    parser.add_argument('--output', type=str, required=True, help='Path to output file')
    return parser.parse_args()


def main():
    """Creates a camera setup file containing camera ids and extrinsic information"""
    # args = parse_args()
    #cameras = initialize_connected_cameras()
    #print(len(cameras))
    #cameras[0].poll_frames()
    pipeline = rs.pipeline()
    pipeline.start()

    try:
        while True:
            # Create a pipeline object. This object configures the streaming camera and owns it's handle
            frames = pipeline.wait_for_frames()
            depth = frames.get_depth_frame()
            if not depth: continue

    finally:
        pipeline.stop()


if __name__ == '__main__':
    main()
