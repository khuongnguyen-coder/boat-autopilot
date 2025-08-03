#!/usr/bin/env python3

import math
import os
import urllib.request
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def __print_debug(msg: str, debug: bool):
    if debug:
        print(msg)

def __deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = int((lon_deg + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return x, y

def __get_bbox_center(lat_min, lon_min, lat_max, lon_max):
    return (lat_min + lat_max) / 2.0, (lon_min + lon_max) / 2.0

def __download_tile(x, y, zoom, tile_dir, user_agent, debug=False):
    tile_path = os.path.join(tile_dir, str(zoom), str(x), f"{y}.png")
    
    if os.path.exists(tile_path):
        __print_debug(f"[✓] Exists: {tile_path}", debug)
        return True  # ← count as handled

    url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
    os.makedirs(os.path.dirname(tile_path), exist_ok=True)
    headers = {"User-Agent": user_agent}
    req = urllib.request.Request(url, headers=headers)

    if debug:
        __print_debug(f"[→] Requesting: {url}", debug)
        __print_debug(f"[→] Headers: {headers}", debug)

    try:
        with urllib.request.urlopen(req) as response, open(tile_path, 'wb') as out_file:
            out_file.write(response.read())
        __print_debug(f"[↓] Downloaded: {tile_path}", debug)
        return True
    except Exception as e:
        __print_debug(f"[!] Failed: {x},{y} (zoom {zoom}) -> {e}", debug)
        return False

def __read_user_agent(file_path = None):
    if file_path != None:
        try:
            with open(file_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"[!] User-Agent file not found: {file_path}")

    return "MyMapDownloader/1.0 (ntkhuong.coder@gmail.com)"

def download_bbox_tiles(bounding_box: dict, zoom_range: dict, tile_dir: str,
                        user_agent: str = None, max_workers: int = 10, debug: bool = False) -> int:
    """
    Download all map tiles for a bounding box and zoom range.

    Returns:
        int: Total number of tiles found or successfully downloaded
    """
    total_handled = 0

    for zoom in range(zoom_range["min"], zoom_range["max"] + 1):
        x_min, y_max = __deg2num(bounding_box["miny"], bounding_box["minx"], zoom)
        x_max, y_min = __deg2num(bounding_box["maxy"], bounding_box["maxx"], zoom)

        __print_debug(f"[i] Zoom {zoom}: x={x_min}→{x_max}, y={y_min}→{y_max}", debug)

        tasks = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for x in range(min(x_min, x_max), max(x_min, x_max) + 1):
                for y in range(min(y_min, y_max), max(y_min, y_max) + 1):
                    tasks.append(executor.submit(__download_tile, x, y, zoom, tile_dir, user_agent, debug))

            for future in as_completed(tasks):
                if future.result():
                    total_handled += 1  # Count downloaded or already exists

    return total_handled

# --- Main CLI ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download raster tiles for a bounding box and zoom range")
    parser.add_argument("--lat-min", type=float, required=True)
    parser.add_argument("--lon-min", type=float, required=True)
    parser.add_argument("--lat-max", type=float, required=True)
    parser.add_argument("--lon-max", type=float, required=True)
    parser.add_argument("--zoom-min", type=int, required=True)
    parser.add_argument("--zoom-max", type=int, required=True)
    parser.add_argument("--output", type=str, default="tiles")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--ua-file", type=str, default="user_agent.inc", help="Path to user-agent file")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    user_agent = __read_user_agent(args.ua_file)

    center_lat, center_lon = __get_bbox_center(args.lat_min, args.lon_min, args.lat_max, args.lon_max)
    __print_debug(f"[i] Center: lat={center_lat:.6f}, lon={center_lon:.6f}", args.debug)

    bbox = {
        "minx": args.lon_min,
        "miny": args.lat_min,
        "maxx": args.lon_max,
        "maxy": args.lat_max,
    }

    zoom_range = {
        "min": args.zoom_min,
        "max": args.zoom_max,
    }

    total = download_bbox_tiles(
        bounding_box=bbox,
        zoom_range=zoom_range,
        tile_dir=args.output,
        user_agent=user_agent,
        max_workers=args.workers,
        debug=args.debug
    )

    print(f"\n✅ Total tiles downloaded: {total}")
