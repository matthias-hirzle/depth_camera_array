from typing import List, Tuple

import numpy as np
from pyrealsense2 import pyrealsense2 as rs


class Camera:
    def __init__(self, device_id: str, context: rs.context):
        resolution_width = 1280
        resolution_height = 720
        frame_rate = 30

        self._device_id = device_id
        self._context = context

        self._pipeline = rs.pipeline()
        self._config = rs.config()
        self._config.enable_device(self._device_id)
        self._config.enable_stream(rs.stream.depth, resolution_width, resolution_height, rs.format.z16, frame_rate)
        self._config.enable_stream(rs.stream.color, resolution_width, resolution_height, rs.format.bgr8, frame_rate)

        self._pipeline_profile: rs.pipeline_profile = self._pipeline.start(self._config)
        self._depth_scale = self._pipeline_profile.get_device().first_depth_sensor().get_depth_scale()

    def poll_frames(self) -> rs.composite_frame:
        """Returns a frames object with each available frame type"""
        frames = self._pipeline.wait_for_frames()
        return frames

    def close(self):
        self._pipeline.stop()

    def image_points_to_object_points(self, color_pixels: np.array, frames: rs.composite_frame) -> List[Tuple[float, float, float]]:
        """Calculates the object points for given pixel coordinates of rgb data"""
        color_frame: rs.video_frame = frames.get_color_frame()
        depth_frame: rs.depth_frame = frames.get_depth_frame()

        color_profile = color_frame.get_profile().as_video_stream_profile()
        depth_profile = depth_frame.get_profile().as_video_stream_profile()

        color_intrinsics = color_profile.get_intrinsics()
        depth_intrinsics = depth_profile.get_intrinsics()

        color_to_depth_extrinsics = color_profile.get_extrinsics_to(depth_profile)
        depth_to_color_extrinsics = depth_profile.get_extrinsics_to(color_profile)

        depth_pixels = [
            rs.rs2_project_color_pixel_to_depth_pixel(
                data=depth_frame.get_data(),
                depth_scale=self._depth_scale,
                depth_min=0.1,
                depth_max=10.0,
                depth_intrin=depth_intrinsics,
                color_intrin=color_intrinsics,
                depth_to_color=depth_to_color_extrinsics,
                color_to_depth=color_to_depth_extrinsics,
                from_pixel=color_pixel
            )
            for color_pixel in color_pixels
        ]

        object_points = []
        for pixel in depth_pixels:
            depth = depth_frame.get_distance(int(round(pixel[0], 0)), int(round(pixel[1], 0)))
            object_points.append(rs.rs2_deproject_pixel_to_point(intrin=depth_intrinsics, pixel=pixel, depth=depth))

        return object_points


def extract_color_image(frames: rs.composite_frame) -> np.ndarray:
    return np.asanyarray(frames.get_color_frame().get_data())


def _find_connected_devices(context):
    devices = []
    for device in context.devices:
        if device.get_info(rs.camera_info.name).lower() != 'platform camera':
            devices.append(device.get_info(rs.camera_info.serial_number))
    return devices


def initialize_connected_cameras() -> List[Camera]:
    context = rs.context()
    device_ids = _find_connected_devices(context)

    devices = [Camera(device_id, context) for device_id in device_ids]
    return devices


def close_connected_cameras(cameras: List[Camera]):
    for camera in cameras:
        camera.close()
