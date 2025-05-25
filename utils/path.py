import os

def utils_path_get_asset(module: str, filename: str) -> str:
    """
    Return the absolute path to an asset file in the assets/ directory.
    This works relative to the project structure.

    Example:
        utils_path_get_asset("map", "icon.png") → /path/to/project/assets/map/icon.png
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    assets_dir = os.path.join(project_root, "assets", module)
    return os.path.join(assets_dir, filename)

def utils_path_get_ui_xml(filename: str) -> str:
    """
    Return the absolute path to an UI xml file in the ui/ directory.
    This works relative to the project structure.

    Example:
        utils_path_get_ui_xml("view.ui") → /path/to/project/ui/view.ui
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    assets_dir = os.path.join(project_root, "ui")
    return os.path.join(assets_dir, filename)