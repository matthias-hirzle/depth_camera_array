from typing import List, Any

import numpy as np
from pyrealsense2 import pyrealsense2 as rs


class Camera:
    def __init__(self, device_id: str, context: rs.context):
        resolution_width = 1280
        resolution_height = 720
        frame_rate = 30
        print(device_id)
        self._device_id = device_id
        self._context = context

        self._pipeline = rs.pipeline()
        self._config = rs.config()
        self._config.enable_device(self._device_id)
        self._config.enable_stream(rs.stream.depth, resolution_width, resolution_height, rs.format.z16, frame_rate)
        # self._config.enable_stream(rs.stream.infrared, 1, resolution_width, resolution_height, rs.format.y8, frame_rate)
        self._config.enable_stream(rs.stream.color, resolution_width, resolution_height, rs.format.bgr8, frame_rate)

        self._pipeline.start(self._config)

        # self._profile = self._pipeline.start(self._config)

    def poll_frames(self) -> rs.composite_frame:
        """Returns a frames object with each available frame type"""
        # streams = self._profile.get_streams()
        # color = rs.pipeline_profile.get_stream(self._profile, rs.stream.color)
        frames = self._pipeline.wait_for_frames()
        # return {
        #     'color': np.asanyarray(frames.get_color_frame().get_data()),
        #     'depth': np.asanyarray(frames.get_depth_frame().get_data())
        # }
        return frames

    def close(self):
        self._pipeline.stop()


def image_points_to_object_points(color_pixels: np.array, frames: rs.composite_frame) -> Any:
    """Calculates the object points for given image points"""
    color: rs.video_frame = frames.get_color_frame()
    depth: rs.depth_frame = frames.get_depth_frame()

    color_profile: rs.stream_profile = color.get_profile()
    depth_profile = depth.get_profile()

    color_intrinsics: rs.intrinsics = color_profile.as_video_stream_profile().get_intrinsics()
    depth_intrinsics: rs.intrinsics = depth_profile.as_video_stream_profile().get_intrinsics()

    color_to_depth_extrinsics: rs.extrinsics = color_profile.get_extrinsics_to(depth_profile)
    depth_to_color_extrinsics: rs.extrinsics = depth_profile.get_extrinsics_to(color_profile)

    depth_pixels = [
        rs.rs2_project_color_pixel_to_depth_pixel(
            data=depth.get_data(),
            depth_scale=1,
            depth_min=0.1,
            depth_max=10,
            depth_intrin=depth_intrinsics,
            color_intrin=color_intrinsics,
            depth_to_color=depth_to_color_extrinsics,
            color_to_depth=color_to_depth_extrinsics,
            from_pixel=color_pixel
        ) for color_pixel in color_pixels
    ]
    return [rs.rs2_deproject_pixel_to_point(depth_intrinsics, pixel) for pixel in depth_pixels]


def extract_color_image(frames: rs.composite_frame) -> np.ndarray:
        return np.asanyarray(frames.get_color_frame().get_data())


def _find_connected_devices(context):
    devices = []
    for device in context.devices:
        if device.get_info(rs.camera_info.name).lower() != 'platform camera':
            devices.append(device.get_info(rs.camera_info.serial_number))
    return devices


def initialize_connected_cameras() -> List[Camera]:
    """
    Enumerate the connected Intel RealSense devices
    Parameters:
    -----------
    context 	   : rs.context()
                     The context created for using the realsense library
    Return:
    -----------
    connect_device : array
                     Array of enumerated devices which are connected to the PC
    """

    context = rs.context()
    device_ids = _find_connected_devices(context)

    devices = [Camera(device_id, context) for device_id in device_ids]
    return devices
