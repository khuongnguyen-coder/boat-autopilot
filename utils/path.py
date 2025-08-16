"""
utils_path.py - Utility functions for resolving project file paths.

This module provides helper functions to consistently locate project
resources such as:
    - UI assets stored under `ui/assets/<module>/`
    - Authentication files stored under `authentication/`

All returned paths are absolute, and required directories are created
automatically when necessary.

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import os


# ********************************************************************************************
def utils_path_get_asset(module: str, filename: str) -> str:
    """
    Return the absolute path to an asset file in the `ui/assets/` directory.

    Args:
        module (str): Subdirectory inside `ui/assets/` (e.g., "map").
        filename (str): Asset file name.

    Returns:
        str: Absolute path to the requested asset.

    Example:
        >>> utils_path_get_asset("map", "icon.png")
        '/path/to/project/ui/assets/map/icon.png'
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    assets_dir = os.path.join(project_root, "ui/assets", module)
    return os.path.join(assets_dir, filename)


# ********************************************************************************************
def utils_path_get_users(filename: str = "users.json") -> str:
    """
    Return the absolute path to a users list file inside `authentication/`.

    If the `authentication/` directory does not exist, it will be created.

    Args:
        filename (str, optional): Name of the users file. Defaults to "users.json".

    Returns:
        str: Absolute path to the users file.

    Raises:
        SystemError: If the path resolution or directory creation fails.

    Example:
        >>> utils_path_get_users("users.json")
        '/path/to/project/authentication/users.json'
    """
    try:
        # Get project root (one level above this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        auth_dir = os.path.join(project_root, "authentication")

        # Ensure the authentication directory exists
        os.makedirs(auth_dir, exist_ok=True)

        # Return absolute path to the file
        return os.path.join(auth_dir, filename)

    except Exception as e:
        raise SystemError(f"Failed to resolve path for users file: {e}")
