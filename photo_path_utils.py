import os


def build_updated_photo_path(new_source_path: str, existing_photo_value: object) -> str:
    """Return the updated path used by photograph-related layers.

    The plugin stores either a folder path in the Source field or a full path in
    Full_Path. When the source path is refreshed, we want existing features to
    keep pointing at the same filename in the new folder whenever possible.
    """
    normalized_new_source_path = str(new_source_path).strip().rstrip("\\/")
    if not normalized_new_source_path:
        return ""

    if existing_photo_value in (None, ""):
        return normalized_new_source_path

    photo_name = os.path.basename(str(existing_photo_value).replace("\\", "/"))
    if not photo_name:
        return normalized_new_source_path

    return f"{normalized_new_source_path}/{photo_name}".replace("\\", "/")


def select_photo_path_field_name(field_names):
    """Return the preferred photo-path attribute field for this layer.

    Some layers expose Full_Path while sampling layers may expose a shorter
    alias such as Photo or Sample Photograph. This helper prefers Full_Path when
    available, otherwise it falls back to the first photo-like field that exists.
    """
    if not field_names:
        return None

    preferred_order = ["Full_Path", "Photo", "Photograph", "Sample Photograph"]
    for preferred_name in preferred_order:
        if preferred_name in field_names:
            return preferred_name

    return None


def build_map_tip_image_expression(source_field_name: str, photo_field_name: str) -> str:
    """Build a QGIS expression for a map-tip image using the available fields."""
    if not source_field_name or not photo_field_name:
        return '""'

    return (
        f'if( "{photo_field_name}" IS NULL OR "{photo_field_name}" = \'\', '
        f'concat(\'file:///\', replace("{source_field_name}", \'\\\\\', \'/\')), '
        f'concat(\'file:///\', replace("{photo_field_name}", \'\\\\\', \'/\')) )'
    )
