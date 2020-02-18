from typing import List

from pyrealsense2 import pyrealsense2 as rs


class DepthCamera:
    def __init__(self, device_id: str, context: rs.context):
        resolution_width = 1280
        resolution_height = 720
        frame_rate = 15
        print(device_id)
        self._device_id = device_id
        self._context = context

        self._pipeline = rs.pipeline(context)
        self._config = rs.config()
        self._config.enable_device(self._device_id)
        self._config.enable_stream(rs.stream.depth, resolution_width, resolution_height, rs.format.z16, frame_rate)
        # self._config.enable_stream(rs.stream.infrared, 1, resolution_width, resolution_height, rs.format.y8, frame_rate)
        self._config.enable_stream(rs.stream.color, resolution_width, resolution_height, rs.format.bgr8, frame_rate)

        self._pipeline.start(self._config)

        # self._profile = self._pipeline.start(self._config)

    def poll_frames(self):
        # streams = self._profile.get_streams()
        # color = rs.pipeline_profile.get_stream(self._profile, rs.stream.color)
        # stream_set = self._pipeline.poll_for_frames()
        # print(len(stream_set))
        frames = self._pipeline.wait_for_frames()
        pass

    def find_qr(self) -> list:
        """finds QR code positions"""
        pass


def _find_connected_devices(context):
    devices = []
    for device in context.devices:
        if device.get_info(rs.camera_info.name).lower() != 'platform camera':
            devices.append(device.get_info(rs.camera_info.serial_number))
    return devices


def initialize_connected_cameras() -> List[DepthCamera]:
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

    devices = [DepthCamera(device_id, context) for device_id in device_ids]
    return devices
