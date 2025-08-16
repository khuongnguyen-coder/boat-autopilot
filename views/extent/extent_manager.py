"""
extent_manager.py - Manager for ENC extent metadata in VNEST Autopilot.

This module is responsible for:
    - Scanning the ENC database directory for `*_metadata.json` files
    - Parsing metadata JSON files into strongly-typed `EncMetadata` dataclasses
    - Managing a list of available ENC extents
    - Providing user-facing utilities (e.g., location list for dropdowns)

Usage:
    from views.extent.extent_manager import ExtentManager

    manager = ExtentManager()
    locations = manager.extent_get_location_list()
    print("Available ENC locations:", locations)

Dependencies:
    - EncMetadata, BoundingBox, Center, ZoomRange (from enc_metadata.py)
    - VNEST_AUTOPILOT_DATABASE_PATH (configured database path)

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

import os
import json

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

from config import VNEST_AUTOPILOT_DATABASE_PATH
from views.extent.enc_metadata import EncMetadata, BoundingBox, Center, ZoomRange


# ********************************************************************************************
class ExtentManager:
    """
    Manager for ENC extent metadata files.

    Responsibilities:
        - Loads all available ENC metadata JSON files.
        - Stores them as `EncMetadata` objects in `self.metadata_list`.
        - Provides helper methods (like `extent_get_location_list()`) 
          for UI components such as dropdowns.

    Attributes:
        metadata_list (List[EncMetadata]): List of loaded ENC metadata objects.
    """
    def __init__(self):
        super().__init__()
        LOG_DEBUG(f"ExtentManager init started with database: {VNEST_AUTOPILOT_DATABASE_PATH}")

        # Load all metadata files from the ENC database directory
        self.metadata_list = load_all_metadata(VNEST_AUTOPILOT_DATABASE_PATH)

        LOG_DEBUG(f"\nTotal loaded: {len(self.metadata_list)} ENC metadata files.")

        # For debug: log available locations
        location_list = self.extent_get_location_list()
        LOG_DEBUG(f"location_list: {location_list}")
    
    def extent_get_location_list(self):
        """
        Build a list of human-readable location names 
        from loaded ENC metadata.

        Returns:
            List[str]: List of location name strings (joined with commas if multiple).
        """
        location_list = []

        if self.metadata_list is None:
            LOG_ERR("Metadata list was invalid.")
        else:
            for metadata in self.metadata_list:
                names = metadata.location_name

                if isinstance(names, list) and names:
                    valid_names = [name.strip() for name in names if isinstance(name, str) and name.strip()]
                    if valid_names:
                        combined = ", ".join(valid_names)
                        location_list.append(combined)
                        LOG_DEBUG(f"[✓] Loaded: {combined}")
                    else:
                        LOG_DEBUG("[✗] Skipped: list had no valid names")
                else:
                    LOG_DEBUG("[✗] Skipped: location_name not a valid list")

        LOG_DEBUG(f"location_list: {location_list}")
        return location_list
# ********************************************************************************************


# ********************************************************************************************
def load_all_metadata(root_dir):
    """
    Scan a directory recursively for ENC metadata JSON files and load them.

    Args:
        root_dir (str): Root directory of ENC database.

    Returns:
        List[EncMetadata]: List of parsed ENC metadata objects.
    """
    metadata_list = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith("_metadata.json"):
                full_path = os.path.join(dirpath, filename)
                try:
                    with open(full_path, "r") as f:
                        data = json.load(f)
                        metadata = EncMetadata(
                            enc_name=data["enc_name"],
                            s57_path=data["s57_path"],
                            file_size_kb=data["file_size_kb"],
                            location_name=data["location_name"],
                            geojson_dir=data["geojson_dir"],
                            layers=data["layers"],
                            bounding_box=BoundingBox(**data["bounding_box"]),
                            bounding_box_with_margin=BoundingBox(**data["bounding_box_with_margin"]),
                            center=Center(**data["center"]),
                            zoom_range=ZoomRange(**data["zoom_range"]),
                            tile_dir=data["tile_dir"],
                            tile_count=data["tile_count"],
                            tile_dir_size_kb=data["tile_dir_size_kb"],
                            created_at=data["created_at"]
                        )
                        metadata_list.append(metadata)
                        LOG_DEBUG(f"[✓] Loaded: {metadata.enc_name} from {full_path}")

                except Exception as e:
                    LOG_ERR(f"[!] Failed to load {full_path}: {e}")
    
    return metadata_list
# ********************************************************************************************
