import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

from gi.repository import GLib

import os
import json

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

from config import VNEST_AUTOPILOT_DATABASE_PATH
from views.extent.enc_metadata import EncMetadata, BoundingBox, Center, ZoomRange

class ExtentManager:
    def __init__(self):
        super().__init__()
        LOG_DEBUG(f"ExtentManager init started with database: {VNEST_AUTOPILOT_DATABASE_PATH}")

        self.metadata_list = load_all_metadata(VNEST_AUTOPILOT_DATABASE_PATH)

        print(f"\nTotal loaded: {len(self.metadata_list)} ENC metadata files.")

def load_all_metadata(root_dir):
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
                    print(f"[!] Failed to load {full_path}: {e}")
    
    return metadata_list
