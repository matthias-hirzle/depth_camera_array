from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl

aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
directory = "/Users/stobko/dev/python/PyCharm/QRCode/aruco_codes/"


def make_12_markers(nx, ny, aruco_dict, directory):
    fig = plt.figure()
    # nx = 4
    # ny = 3
    for i in range(1, nx * ny + 1):
        ax = fig.add_subplot(ny, nx, i)
        img = aruco.drawMarker(aruco_dict, i, 700)

        plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
        ax.axis("off")

        plt.savefig("{}_markers5x5_12pro_plate.pdf".format(directory))


def make_4_markers(nx, ny, aruco_dict, directory, id_nr_start):
    fig = plt.figure()
    # nx = 2
    # ny = 2
    # id_nr_start = 16

    for j in range(1, 5):
        id_nr_start += 4
        for i in range(1, nx * ny + 1):
            ax = fig.add_subplot(ny, nx, i)
            img = aruco.drawMarker(aruco_dict, i + id_nr_start, 700)

            plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
            ax.axis("off")

            plt.savefig("{}_markers5x5_4pro_plate_nr_{}.pdf".format(directory, j))


make_12_markers(x=4, y=3, aruco_dict=aruco_dict, directory=directory)
make_4_markers(x=2, y=2, aruco_dict=aruco_dict, directory=directory, id_nr_start=16)
