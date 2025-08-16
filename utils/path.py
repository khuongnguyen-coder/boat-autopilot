import os

# ********************************************************************************************
def utils_path_get_asset(module: str, filename: str) -> str:
    """
    Return the absolute path to an asset file in the assets/ directory.
    This works relative to the project structure.

    Example:
        utils_path_get_asset("map", "icon.png") → /path/to/project/assets/map/icon.png
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    assets_dir = os.path.join(project_root, "ui/assets", module)
    return os.path.join(assets_dir, filename)
# ********************************************************************************************

# ********************************************************************************************
def utils_path_get_users(filename: str = "users.json") -> str:
    """
    Return the absolute path to a users list file.
    Ensures the 'authentication' directory exists.

    Example:
        utils_path_get_users("users.json") 
        → /path/to/project/authentication/users.json
    """
    try:
        # Get project root (one level above this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        auth_dir = os.path.join(project_root, "authentication")

        # Make sure the authentication directory exists
        os.makedirs(auth_dir, exist_ok=True)

        # Return absolute path to the file
        return os.path.join(auth_dir, filename)

    except Exception as e:
        raise SystemError(f"Failed to resolve path for users file: {e}")

# ********************************************************************************************