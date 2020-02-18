from pyrealsense2 import pyrealsense2 as rs


def initialize_connected_cameras() -> list:
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
    devices = []
    for device in context.devices:
        if device.get_info(rs.camera_info.name).lower() != 'platform camera':
            devices.append(device.get_info(rs.camera_info.serial_number))
    return devices


class DepthCamera:
    def __init__(self, device_id: str):
        self.pipeline = rs.pipeline()
        self.config = rs.config
        pass
