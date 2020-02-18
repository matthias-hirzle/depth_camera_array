from pyrealsense2 import pyrealsense2 as rs

class DepthCamera:
    def __init__(self, device_id: str):
        self.pipeline = rs.pipeline()
        self.config = rs.config
        pass

