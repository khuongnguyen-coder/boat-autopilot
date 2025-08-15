#!/usr/bin/env python3

import os
import sys
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from osgeo import ogr

ogr.UseExceptions()  # Avoid GDAL 4.0 warning

def __print_debug(msg, debug=False):
    if debug:
        print(f"[GEOJSON] {msg}")

def __get_layer_names(s57_path, debug=False):
    result = subprocess.run(
        ["ogrinfo", "-ro", "-q", s57_path],
        capture_output=True, text=True, check=True
    )
    
    layers = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            layer = line.split(":", 1)[1].split("(")[0].strip()
            layers[layer] = True  # default: visible

    __print_debug(f"Layers found with flags: {layers}", debug)
    return layers

def __export_layer_to_geojson(s57_path, layer_name, output_path, debug=False):
    raw_path = output_path.with_suffix(".raw.json")
    final_path = output_path.with_suffix(".geojson")

    __print_debug(f"Exporting layer '{layer_name}' to {raw_path}", debug)
    subprocess.run(["ogr2ogr", "-f", "GeoJSON", str(raw_path), s57_path, layer_name],
                   check=True)

    with open(raw_path) as f:
        parsed = json.load(f)

    with open(final_path, "w") as f:
        json.dump(parsed, f, indent=2)

    raw_path.unlink()  # delete .raw.json
    __print_debug(f"Saved final GeoJSON to {final_path}", debug)

def export_geojson(s57_path, output_dir, debug: bool = False):
    """
    Export all layers in an S57 ENC file to individual GeoJSON files.

    Args:
        s57_path (str): Path to S-57 ENC file (.000)
        output_dir (str): Directory to save output GeoJSON files
        debug (bool): Enable verbose debug output
    """
    if not os.path.isfile(s57_path):
        print(f"Error: File not found: {s57_path}")
        sys.exit(2)

    os.makedirs(output_dir, exist_ok=True)
    __print_debug(f" ** Input file: {s57_path}", debug)
    __print_debug(f" ** Output directory: {output_dir}", debug)

    layers = __get_layer_names(s57_path, debug=debug)
    if not layers:
        print("Warning: No layers found in file.")
        sys.exit(3)

    if debug:
        print("Found layers:")
        for layer in layers:
            print(f"  - {layer}")
        print()

    for layer_name in layers.keys():
        __print_debug(f"Processing layer: {layer_name}", debug)
        output_path = Path(output_dir) / layer_name
        __export_layer_to_geojson(s57_path, layer_name, output_path, debug=debug)
        __print_debug(f"Saved: {output_path.with_suffix('.geojson')}", debug)


    return layers

# Compile pattern to match provinces/districts (Vietnamese + English)
province_district_pattern = re.compile(
    r"\b(tỉnh|thành phố|quận|huyện|thị xã|province|district|city|municipality)\b",
    re.IGNORECASE
)

def is_province_or_district(name: str) -> bool:
    return bool(province_district_pattern.search(name))

def extract_named_locations(s57_path: str, debug: bool = False) -> list[str]:
    """
    Extract and return province/district names from an ENC (S-57) file.

    Parameters:
        s57_path (str): Path to the ENC .000 file (usually the base file of an S-57 dataset).
        debug (bool): Enable verbose output.

    Returns:
        list[str]: List of found location names (province and district level).
    """

    if not os.path.isfile(s57_path):
        print(f"Error: File not found: {s57_path}")
        sys.exit(2)

    dataset = ogr.Open(s57_path)
    if not dataset:
        print(f"Error: Unable to open dataset: {s57_path}")
        sys.exit(1)

    layer_names = __get_layer_names(s57_path, debug=debug)
    if not layer_names:
        print("Warning: No layers found in file.")
        sys.exit(3)

    if debug:
        print("Found layers:")
        for name in layer_names:
            print(f"  - {name}")
        print()

    location_names = set()  # Use set to avoid duplicates

    for name in layer_names:
        layer = dataset.GetLayerByName(name)
        if not layer:
            __print_debug(f"Skipping missing layer: {name}", debug)
            continue

        __print_debug(f"Processing layer: {name}", debug)

        for feature in layer:
            if "OBJNAM" in feature.keys():
                objnam = feature.GetField("OBJNAM")
                if objnam and is_province_or_district(objnam):
                    location_names.add(objnam)
                    __print_debug(f"Found name: {objnam} in layer: {name}", debug)

    return sorted(location_names)

# --- Main entry point ---
if __name__ == "__main__":
    args = sys.argv[1:]
    if not (2 <= len(args) <= 3):
        print("Usage: export_geojson.py <S57_FILE.000> <output_directory> [--debug]")
        sys.exit(1)

    s57_file = args[0]
    out_dir = args[1]
    debug = len(args) == 3 and args[2] == "--debug"

    if not debug:
        print("Hint: Set DEBUG=1 or use --debug to enable verbose output")

    # export_geojson(s57_file, out_dir, debug=debug)
    location_names = extract_named_locations(s57_file, debug=debug)
    print(f"Found location_names: {location_names}")
