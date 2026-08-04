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
