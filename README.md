# Depth Camera Array
## Overview
This software allows to calibrate multiple RealSense devices to one world-coordinate-system. Objects can be measured and 
exported in *.ply format.

## Installation Instructions
### Prerequisites
Install the [Intel RealSense SDK 2.0](https://www.intelrealsense.com/developers/) for your platform.
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
### Prerequisites
- Follow the [installation instructions](#installation-instructions) above
- Activate your virtual environment: `source venv/bin/activate`
- Create the aruco calibration targets:
    1. run script `./create_calibration_targets.sh` to create PDF files. You can pass two optional arguments: 
        - `--target_count=<int>`: Number of targets to calculate relative extrinsic between cameras. 
        If not set, `5` targets will be created.
        - `--data_dir=<str>`: A path to the directory where the created target files will be stored. If the directory 
        does not exist, it will be created. If not set, `./data/` will be used as directory.
    1. As result of the previous step you'll get one `bottom_target.pdf` and multiple 
    `relative_target_..._front.pdf` files. For each `...front.pdf` file, one `...back.pdf` will be created. 
    Print the files and stick the corresponding sheets together. Make sure that the corners of the corresponding aruco 
    markers match each other exactly.
    ![Relative Target](https://drive.google.com/uc?export=view&id=108rJgdewXZShswhkx3LOTUoS4TjCuWWP)
    1. Position the _Relative Targets_ so that they are in the field of view of every camera.
    1. Position the _Bottom Target_ on the ground. This target describes the axis directions and the center of the 
    world-coordinate-system you want to transform to. It must be in the view of at least one camera.
    ![Bottom Target](https://drive.google.com/uc?export=view&id=1o_QjE5uSYpaoqQz28YgRcqxZjMs779cs)
> Use the RealSense Viewer tool to check if the view of cameras.    
### Calibration
1. Detect aruco markers
1. Calibrate extrinsic

### Measurement
1. Measure point clouds in defined cylinder area and dump it as .ply file