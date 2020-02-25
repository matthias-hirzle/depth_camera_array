import unittest
from unittest import mock

import numpy as np

from depth_camera_array.perform_aruco_detection import detect_aruco_targets, determine_aruco_center


def detectMarkers_patch(*args):
    return (
        [
            np.array([[[382., 405.], [601., 405.], [601., 624.], [382., 624.]]], dtype=np.float32),
            np.array([[[120., 405.], [338., 405.], [338., 624.], [120., 624.]]], dtype=np.float32),
            np.array([[[382., 102.], [601., 102.], [601., 321.], [382., 321.]]], dtype=np.float32),
            np.array([[[120., 102.], [338., 102.], [338., 321.], [120., 321.]]], dtype=np.float32)
        ],
        np.array([[7], [6], [5], [4]], dtype=np.int32),
        [
            np.array([[[437., 553.], [485., 555.], [483., 601.], [436., 599.]]], dtype=np.float32),
            np.array([[[244., 500.], [275., 499.], [276., 529.], [245., 529.]]], dtype=np.float32),
            np.array([[[437., 250.], [512., 249.], [515., 296.], [438., 298.]]], dtype=np.float32),
            np.array([[[532., 124.], [578., 126.], [576., 173.], [530., 172.]]], dtype=np.float32)
        ]
    )


EXPECTED_DETECT_ARUCO_TARGETS = (
    [
        np.array([[382., 405.], [601., 405.], [601., 624.], [382., 624.]], dtype=np.float32),
        np.array([[120., 405.], [338., 405.], [338., 624.], [120., 624.]], dtype=np.float32),
        np.array([[382., 102.], [601., 102.], [601., 321.], [382., 321.]], dtype=np.float32),
        np.array([[120., 102.], [338., 102.], [338., 321.], [120., 321.]], dtype=np.float32)
    ], [7, 6, 5, 4])


#     aruco_corners, aruco_ids, _ = aruco.detectMarkers(rgb_image, aruco.Dictionary_get(aruco.DICT_5X5_250))
class MyTestCase(unittest.TestCase):
    @mock.patch('cv2.aruco.detectMarkers', side_effect=detectMarkers_patch)
    def test_detect_aruco_targets(self, *args):
        aruco_corners, aruco_ids = detect_aruco_targets(None)
        self.assertListEqual(EXPECTED_DETECT_ARUCO_TARGETS[1], aruco_ids)
        np.testing.assert_array_equal(EXPECTED_DETECT_ARUCO_TARGETS[0], aruco_corners)

    def test_determine_aruco_center(self):
        expected = np.array([10, 10])
        corners = np.array([[12, 11], [11, 8], [8, 9], [9, 12]])
        result = determine_aruco_center(corners)
        np.testing.assert_array_equal(expected, result)


if __name__ == '__main__':
    unittest.main()
