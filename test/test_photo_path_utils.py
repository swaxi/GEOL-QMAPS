import unittest

from photo_path_utils import build_updated_photo_path


class PhotoPathUtilsTests(unittest.TestCase):
    def test_uses_filename_from_existing_photo_reference(self):
        self.assertEqual(
            build_updated_photo_path(r"C:\\photos", r"D:\\old\\IMG_001.jpg"),
            r"C:\\photos\\IMG_001.jpg",
        )

    def test_returns_directory_when_photo_reference_is_missing(self):
        self.assertEqual(build_updated_photo_path(r"C:\\photos", ""), r"C:\\photos")


if __name__ == "__main__":
    unittest.main()
