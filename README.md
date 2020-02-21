# Depth Camera Array
## Overview
This software allows to calibrate multiple RealSense devices to one world-coordinate-system. Objects can be measured and 
exported in *.ply format.

## Installation Instructions
## Prerequisites
Install the [Intel RealSense SDK 2.0](https://dev.intelrealsense.com/docs/installation) for your platform.
### Install manually
1. Clone the repository:
```bash
git clone https://github.com/matthias-hirzle/depth_camera_array.git && cd depth_camera_array
```
2. Create a new virtual environment:
```bash
python3 -m venv venv
```
3. Activate the virtual environment:
```bash
source venv/bin/activate
```
4. Install requirements:
```bash
pip install -r requirements.txt
```

### Install via pip
```bash
pip install git+https://github.com/matthias-hirzle/depth_camera_array.git@master#egg=depth_camera_array
```
## Usage
1. Detect aruco markers
1. Calibrate extrinsic
1. Measure point clouds in defined cylinder area and dump it as .ply file