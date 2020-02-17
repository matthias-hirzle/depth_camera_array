import setuptools

VERSION = '0.1.0'

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

with open('requirements.txt', 'r') as f:
    REQUIREMENTS = [
        req.split('#')[0] for req in list(filter(lambda item: item not in ['', '\n'], f.read().split('\n')))]

setuptools.setup(
    name='depth_camera_array',
    version=VERSION,
    author='Matthias Hirzle, Joshua Reimer, Stoyan Georgiev',
    author_email='hima1021@hs-karlsruhe.de, rejo1020@hs-karlsruhe.de, gest1019@hs-karlsruhe.de',
    description='Tool to handle depth camera arrays',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/matthias-hirzle/DepthCamera-Array',
    packages=setuptools.find_packages(),
    install_requires=REQUIREMENTS,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
