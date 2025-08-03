#!/usr/bin/env python3

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

def __print_debug(msg, debug=False):
    if debug:
        print(f"[GEOJSON] {msg}")

def __get_layer_names(s57_path, debug=False):
    result = subprocess.run(
        ["ogrinfo", "-ro", "-q", s57_path],
        capture_output=True, text=True, check=True
    )
    layers = []
    for line in result.stdout.splitlines():
        if ":" in line:
            layer = line.split(":", 1)[1].split("(")[0].strip()
            layers.append(layer)
    __print_debug(f"Layers found: {layers}", debug)
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

    for layer in layers:
        __print_debug(f"Processing layer: {layer}", debug)
        output_path = Path(output_dir) / layer
        __export_layer_to_geojson(s57_path, layer, output_path, debug=debug)
        __print_debug(f"Saved: {output_path.with_suffix('.geojson')}", debug)

    return layers

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

    export_geojson(s57_file, out_dir, debug=debug)
