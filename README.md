# DepthCamera-Extrinsics-Calibration
## Installation Instructions
1. Clone the repository
```bash
git clone https://github.com/matthias-hirzle/depth_camera_array.git && cd depth_camera_array
```
1. Create a virtual environment
```bash
python3 -m venv venv
```
> Maybe you need to install venv package first: `pip3 install venv`
1. Activate the virtual environment
```bash
source venv/bin/activate
```
1. Install requirements
```bash
pip install -r requirements.txt
```

Or use the package directly in your project:
```bash
pip install git+https://github.com/matthias-hirzle/depth_camera_array.git@master#egg=depth_camera_array
```