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
#### Create the aruco calibration targets:
Activate your virtual environment and run script `./create_calibration_targets.sh` to create the calibration targets as 
PDF files. You can pass two optional arguments: 
- `--target_count=<int>`: Number of targets to calculate relative extrinsic between cameras. 
If not set, `5` targets will be created.
- `--data_dir=<str>`: A path to the directory where the created target files will be stored to. If the directory 
does not exist, it will be created. If not set, `./data/` will be used as directory.

As result of executing the script you'll get one `bottom_target.pdf` and multiple `relative_target_..._front.pdf` files.
For each `...front.pdf` file, one `...back.pdf` will be created. Those pdf files should look similar to the images 
below.  
![bottom_target](https://user-images.githubusercontent.com/44577643/75158186-e2d8a500-5715-11ea-8d8b-ccb845796f17.png)
![relative_target](https://user-images.githubusercontent.com/44577643/75158326-292e0400-5716-11ea-9479-fc4c3a662982.png)
Print the files and stick the corresponding sheets with realtive targets together. Make sure that the corners of the 
corresponding aruco markers match each other exactly.

### Calibration
1. **Place the calibration targets**: In the view of each camera should be minimum 3 arucos of the _Relative Targets_. 
In the view of one camrea should be every _Relative Target_ and also the _Bottom Target_. This camera will be 
automatically detected as _Base Camera_. Place the _Bottom Target_ according to the desired orientation of the world 
coordinate system. The more aruco targets in the view of each camera the better is the result of your calibration. 
![camera_array](https://user-images.githubusercontent.com/44577643/75285967-e18fa100-5817-11ea-9cc0-15a448225066.png)
> Use the RealSense Viewer tool to check the view of cameras.    
1. **Detect aruco markers:**
Connect your RealSense devices to your computer. Make sure that you use USB 3 connections. Not all RealSense devices 
need to be connected at the same time. It is also possible to run the target detection for separate camera 
groups one after another. This makes sense if you don't have enough USB 3.0 ports or if your USB-cables are too short to 
connect all devices at once. Run the following script for each camera group connected to your computer:
```bash
./perform_aruco_detection.sh
```
This will create a `<device_id>_reference_.json` file containing information about the detected aruco markers for each 
connected device and store them the `./data/` folder. Pass the argument `--remove_old_data` to remove obsolete files 
created by a previous calibration with another camera setup in that folder. You can also choose the destination 
directory for your `...refernce_points.json` files by passing the argument `--data_dir=<path>`.
> Do not move the calibration targets until you ran the detection for every device in your RealSense array. 
1. **Calibrate extrinsic:**
After detecting the positions of the calibration targets run the following script:
```bash
./perform_calibration
```
This will load the previously created `<camera_id>_reference_points.json` files and use them to determine the extrinsic 
parameters for each device. If these files are not located in the default `./data/` directory, pass the argument 
`--data_dir=<path>` to define the location. This script creates a file `camera_array.json` that contains extrinsic 
parameters as 4x4 homogeneous transformation matrices for each device.
> Use the RealSense Viewer tool to check the type of usb connection.
### Measurement
1. Measure point clouds in defined cylinder area and dump it as .ply file