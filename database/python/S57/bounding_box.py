#!/usr/bin/env python3

import sys
import os
import subprocess
import re
from typing import Tuple, List, Optional

DEBUG = os.environ.get("DEBUG") == "1"

def __print_debug(msg, enabled=True):
    if enabled:
        print(f"[BOUNDING BOX] {msg}")

def __get_layers(s57_file: str, debug: bool = False) -> List[str]:
    try:
        output = subprocess.check_output(["ogrinfo", s57_file], text=True)
        layers = []
        for line in output.splitlines():
            match = re.match(r"^\d+:\s+(\S+)", line)
            if match:
                layer = match.group(1)
                if layer not in ("DSID", "DSSI", "DSPM", "CATD"):
                    layers.append(layer)
        __print_debug(f"Found layers: {layers}", debug)
        return layers
    except subprocess.CalledProcessError as e:
        print(f"Error getting layers: {e}")
        return []

def __extract_extent(s57_file: str, layer: str) -> Optional[Tuple[float, float, float, float]]:
    try:
        output = subprocess.check_output(["ogrinfo", s57_file, layer, "-al", "-so"], text=True)
        for line in output.splitlines():
            if "Extent:" in line:
                coords = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if len(coords) == 4:
                    return tuple(map(float, coords))
    except subprocess.CalledProcessError:
        pass
    return None

def bounding_box(s57_file: str, debug: bool = False) -> Optional[dict]:
    """
    Extract the largest bounding box from the geometry layers in an S-57 ENC file.

    Args:
        s57_file (str): Path to the S-57 (.000) file.
        debug (bool): If True, print debug output to console.

    Returns:
        dict with keys 'minx', 'miny', 'maxx', 'maxy' if successful,
        or None if no valid bounding box is found.

    Example:
        bbox = get_bounding_box("ENC_ROOT/V25AT001.000", debug=True)
    """
    layers = __get_layers(s57_file, debug=debug)
    if debug:
        print("Detected layers:")
        for layer in layers:
            print(f"  - {layer}")
        print()

    max_area = 0
    max_bbox = None
    max_layer = None

    for layer in layers:
        extent = __extract_extent(s57_file, layer)
        if extent:
            minx, miny, maxx, maxy = extent
            area = (maxx - minx) * (maxy - miny)
            __print_debug(f"Layer: {layer:<20} Area: {area:.8f}  Extent: ({minx}, {miny}) - ({maxx}, {maxy})", debug)
            if area > max_area:
                max_area = area
                max_bbox = extent
                max_layer = layer
        else:
            __print_debug(f"Skipping layer {layer} (no valid extent)", debug)

    if max_bbox:
        minx, miny, maxx, maxy = max_bbox
        return {
            "minx": minx,
            "miny": miny,
            "maxx": maxx,
            "maxy": maxy,
        }
    else:
        __print_debug(f"No valid bounding box found in any layer of {s57_file}.", debug)
        return None

def bounding_box_padded(bbox: dict, margin_percent: float = 0.02, debug: bool = False) -> Optional[dict]:
    """
    Apply padding to a given bounding box.

    Args:
        bbox (dict): Dictionary with keys 'minx', 'miny', 'maxx', 'maxy'.
        margin_percent (float): Margin ratio to expand box (e.g. 0.02 = 2%). Default is 0.02.
        debug (bool): Enable verbose debug output. Default is False.

    Returns:
        dict: New dictionary with padded bounding box values.
              Keys: 'minx', 'miny', 'maxx', 'maxy'.
        None: If bbox is invalid or missing keys.

    Example:
        bbox = get_bounding_box("V25AT001.000")
        padded = get_padded_bounding_box(bbox, margin_percent=0.05)
    """
    if not bbox or not all(k in bbox for k in ("minx", "miny", "maxx", "maxy")):
        __print_debug("Invalid bbox input", debug)
        return None

    width = bbox["maxx"] - bbox["minx"]
    height = bbox["maxy"] - bbox["miny"]
    margin_x = width * margin_percent
    margin_y = height * margin_percent

    padded = {
        "minx": bbox["minx"] - margin_x,
        "miny": bbox["miny"] - margin_y,
        "maxx": bbox["maxx"] + margin_x,
        "maxy": bbox["maxy"] + margin_y,
    }

    __print_debug(f"Padded bounding box: {padded}", debug)
    return padded

def bounding_box_get_center(bbox: dict) -> Optional[dict]:
    """
    Calculate the center point of a bounding box.

    Args:
        bbox (dict): Dictionary with keys 'minx', 'miny', 'maxx', 'maxy'

    Returns:
        dict: Dictionary with keys 'x' and 'y' representing the center point
        None: If input is invalid
    """
    if not bbox or not all(k in bbox for k in ("minx", "miny", "maxx", "maxy")):
        return None

    return {
        "lon": (bbox["minx"] + bbox["maxx"]) / 2,
        "lat": (bbox["miny"] + bbox["maxy"]) / 2
    }

def bounding_box_zoom_range() -> dict:
    """
    Return a fixed zoom level range for the bounding box.

    Returns:
        dict: Dictionary with 'min' and 'max' zoom levels
    """
    return {
        "min": 10,
        "max": 19
    }

# --- CLI mode ---
if __name__ == "__main__":
    args = sys.argv[1:]
    if not (1 <= len(args) <= 2):
        print("Usage: python get_bounding_box.py <path_to_s57_file> [--debug]")
        print("Set DEBUG=1 in the environment to show detailed output")
        sys.exit(1)

    s57_file = args[0]
    if len(args) == 2 and args[1] == "--debug":
        DEBUG = True

    if not DEBUG:
        print("Hint: Set DEBUG=1 or use --debug to enable verbose output")

    bbox = bounding_box(s57_file, debug=DEBUG)
    if bbox:
        print("Bounding box:")
        print(bbox)
    else:
        sys.exit(4)

    padded_bbox = bounding_box(bbox, debug=DEBUG)
    if padded_bbox:
        print("Bounding box padded with 20%:")
        print(padded_bbox)
    else:
        sys.exit(4)

    sys.exit(0)
