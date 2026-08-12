import unittest

from photo_path_utils import (
    build_map_tip_image_expression,
    build_updated_photo_path,
    select_photo_path_field_name,
)


class PhotoPathUtilsTests(unittest.TestCase):
    def test_uses_filename_from_existing_photo_reference(self):
        self.assertEqual(
            build_updated_photo_path(r"C:\\photos", r"D:\\old\\IMG_001.jpg"),
            r"C:\\photos\\IMG_001.jpg",
        )

    def test_returns_directory_when_photo_reference_is_missing(self):
        self.assertEqual(build_updated_photo_path(r"C:\\photos", ""), r"C:\\photos")

    def test_prefers_full_path_field_when_present(self):
        self.assertEqual(
            select_photo_path_field_name(["Source", "Full_Path", "Photograph"]),
            "Full_Path",
        )

    def test_falls_back_to_photo_field_for_sampling_layers(self):
        self.assertEqual(select_photo_path_field_name(["Source", "Photo"]), "Photo")

    def test_builds_map_tip_expression_for_photo_field(self):
        expression = build_map_tip_image_expression("Source", "Photo")
        self.assertIn('"Photo"', expression)
        self.assertIn('"Source"', expression)


if __name__ == "__main__":
    unittest.main()
