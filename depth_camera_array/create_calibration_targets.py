import argparse
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from cv2 import aruco

from depth_camera_array.utilities import DEFAULT_DATA_DIR, create_if_not_exists


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Creates calibration aruco targets for extrinsic calibration between multiple '
                                     'RealSense devices and a world coordinate system.')
    parser.add_argument('--data_dir', type=lambda item: create_if_not_exists(item), default=DEFAULT_DATA_DIR,
                        help='A path to the directory where the created target files will be stored. If the directory '
                             'does not exist, it will be created. If not set, ./data/ will be used as directory.')
    parser.add_argument('--target_count', type=int, default=5,
                        help='Number of targets to calculate relative extrinsic between cameras. If not set, 5 targets '
                             'will be created.')
    return parser.parse_args()


def create_bottom_target(data_dir):
    shape = (3, 4,)
    fig = plt.figure()
    fig.suptitle('Bottom Targets (1-3)', color='gray')
    for index, aruco_id in [(1, 2,), (4, 1,), (9, 3,)]:
        ax = fig.add_subplot(*shape, index)
        img = aruco.drawMarker(aruco.Dictionary_get(aruco.DICT_5X5_250), index, 700)
        plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
        ax.set_title(aruco_id, color='gray')
        ax.axis('off')

    # Z-Axis
    ax = fig.add_subplot(*shape, 5)
    ax.annotate('', xy=(0.5, 0), xytext=(0.5, 1), arrowprops=dict(edgecolor='gray', facecolor='gray', shrink=0.05))
    ax.axis('off')
    ax.text(0.3, 0.5, 'Z', color='gray')
    plt.savefig(os.path.join(data_dir, 'bottom_target.pdf'))

    # X-Axis
    ax = fig.add_subplot(3, 3, 2)
    ax.annotate('', xy=(1, 0.5), xytext=(0, 0.5), arrowprops=dict(edgecolor='gray', facecolor='gray', shrink=0.05))
    ax.text(0.45, 0.6, 'X', color='gray')
    ax.axis('off')
    plt.savefig(os.path.join(data_dir, 'bottom_target.pdf'))


def create_relative_targets(target_count, min_aruco_id, data_dir):
    shape = (2, 3,)
    aruco_id = min_aruco_id
    for i in range(target_count):
        fig = plt.figure()
        fig.suptitle(f'Front Targets ({aruco_id}-{aruco_id + 3})', color='gray')
        for k in [1, 2, 4, 5]:
            ax = fig.add_subplot(*shape, k)
            img = aruco.drawMarker(aruco.Dictionary_get(aruco.DICT_5X5_250), aruco_id, 700)
            plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
            ax.axis('off')
            ax.set_title(aruco_id, color='gray')
            aruco_id += 1

        plt.savefig(os.path.join(data_dir, f'relative_target_{aruco_id - 4}_to_{aruco_id-1}_front.pdf'))

    aruco_id = min_aruco_id
    for i in range(target_count):
        fig = plt.figure()
        fig.suptitle(f'Back Targets ({aruco_id}-{aruco_id + 3})', color='gray')
        for k in [3, 2, 6, 5]:
            ax = fig.add_subplot(*shape, k)
            img = aruco.drawMarker(aruco.Dictionary_get(aruco.DICT_5X5_250), aruco_id, 700)
            plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
            ax.axis('off')
            ax.set_title(aruco_id, color='gray')
            aruco_id += 1

        plt.savefig(os.path.join(data_dir, f'relative_target_{aruco_id - 4}_to_{aruco_id - 1}_back.pdf'))

def main():
    args = parse_args()
    create_bottom_target(data_dir=args.data_dir)
    create_relative_targets(args.target_count, 4, args.data_dir)


if __name__ == '__main__':
    main()
