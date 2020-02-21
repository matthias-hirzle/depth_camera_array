import argparse
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from cv2 import aruco

from depth_camera_array.utilities import DEFAULT_DATA_DIR, create_if_not_exists


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Creates aruco targets')
    parser.add_argument('--data_dir', type=lambda item: create_if_not_exists(item), default=DEFAULT_DATA_DIR,
                        help='Data location to load and dump config files')
    parser.add_argument('--target_count', type=int, default=5, help='Number of relative targets (2x2 arucos)')
    return parser.parse_args()


def create_bottom_target(data_dir):
    shape = (3, 4,)
    fig = plt.figure()
    fig.suptitle('Bottom Target (1-3)', color='gray')
    for index, aruco_id in [(1, 1,), (4, 2,), (12, 3,)]:
        ax = fig.add_subplot(*shape, index)
        img = aruco.drawMarker(aruco.Dictionary_get(aruco.DICT_5X5_250), index, 700)
        plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
        ax.axis('off')

    # Z-Axis
    ax = fig.add_subplot(*shape, 8)
    ax.annotate('', xy=(0.5, 0), xytext=(0.5, 1), arrowprops=dict(edgecolor='gray', facecolor='gray', shrink=0.05))
    ax.axis('off')
    ax.text(0.6, 0.5, 'Z', color='gray')
    plt.savefig(os.path.join(data_dir, 'bottom_target.pdf'))

    # X-Axis
    ax = fig.add_subplot(3, 3, 2)
    ax.annotate('', xy=(0, 0.5), xytext=(1, 0.5), arrowprops=dict(edgecolor='gray', facecolor='gray', shrink=0.05))
    ax.text(0.5, 0.6, 'X', color='gray')
    ax.axis('off')
    plt.savefig(os.path.join(data_dir, 'bottom_target.pdf'))


def create_relative_targets(target_count, min_aruco_id, data_dir):
    shape = (2, 3,)
    for i in range(target_count):
        fig = plt.figure()
        fig.suptitle(f'Relative Target ({min_aruco_id}-{min_aruco_id + 4})', color='gray')
        for k in [1, 2, 4, 5]:
            ax = fig.add_subplot(*shape, k)
            img = aruco.drawMarker(aruco.Dictionary_get(aruco.DICT_5X5_250), min_aruco_id, 700)
            plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
            ax.axis("off")
            ax.set_xlabel(min_aruco_id)
            min_aruco_id += 1

        plt.savefig(os.path.join(data_dir, f'relative_target_{min_aruco_id - 5}_to_{min_aruco_id - 1}.pdf'))


def main():
    args = parse_args()
    create_bottom_target(data_dir=args.data_dir)
    create_relative_targets(args.target_count, 4, args.data_dir)


if __name__ == '__main__':
    main()
