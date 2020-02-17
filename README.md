# DepthCamera-Extrinsics-Calibration
## Installation Instructions
### Install manually
1. Clone the repository:
```bash
git clone https://github.com/matthias-hirzle/depth_camera_array.git && cd depth_camera_array
```
2. Create a virtual new environment:
```bash
python3 -m venv venv
```
> Maybe you need to install venv package first: `pip3 install venv`
3. Activate the virtual environment:
```bash
source venv/bin/activate
```
4. Install requirements:
```bash
pip install -r requirements.txt
```
### Install via pip
:
```bash
pip install git+https://github.com/matthias-hirzle/depth_camera_array.git@master#egg=depth_camera_array
```