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
### Calibration Prerequisites
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
    ![relative_target](https://user-images.githubusercontent.com/44577643/75158326-292e0400-5716-11ea-9479-fc4c3a662982.png)
    1. Position the _Relative Targets_ so that they are in the field of view of every camera.
    1. Position the _Bottom Target_ on the ground. This target describes the axis directions and the center of the 
    world-coordinate-system you want to transform to. It must be in the view of at least one camera.
    ![bottom_target](https://user-images.githubusercontent.com/44577643/75158186-e2d8a500-5715-11ea-8d8b-ccb845796f17.png)
> Use the RealSense Viewer tool to check the view of cameras.    

### Calibration
1. **Activate your virtual environment:** `source venv/bin/activate`
1. **Detect aruco markers:**
Connect your RealSense devices to your computer. Make sure that you use USB 3 connections. You do not need to connect 
each RealSense device to your computer at once. It is also possible to run the target detection for separate camera 
groups one after another. This makes sense if you don't have enough USB 3.0 ports or if your USB-cables are to short to 
connect each camera at once. This step will create a `<device_id>_reference_points.json` file for every connected camera 
    - Run the script `./perform_aruco_detection.sh --remove_old_data` for the first connected camera group of your 
    RealSense array. This will delete `<device_id>_reference_points.json` files of previous target detections. This is 
    necessary to determine correct extrinsic without wrong data in the next step.
    - Run `perform_aruco_detection.sh` without argument `--remove_old_data` for each other camera group. 
1. **Calibrate extrinsic:**
The previously created `<camera_id_reference_points.json>` files containing information about detected 
camera-coordinates of aruco markers are loaded and used to determine the extrinsic parameters. 
Run the script `./perform_calibration` to create a `camera_array.json` file. This file contains the extrinsic 
parameters to the world-coordinate-system defined through the position of the bottom-target. The extrinsic 
parameters are stored as 4x4 homogeneous transformation matrix. 

### Measurement
1. Measure point clouds in defined cylinder area and dump it as .ply file