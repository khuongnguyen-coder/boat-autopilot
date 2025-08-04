import argparse
import os
import json
from datetime import datetime

from utils.helper import *
from S57.export_geojson import *
from S57.bounding_box import *
from S57.bounding_box import *
from map.raster_tile_download import *

USER_AGENT="MyMapDownloader/1.0 (ntkhuong.coder@gmail.com)"

def metadata_save(metadata: dict):
    """
    Save metadata to a JSON file.

    Args:
        metadata (dict): Metadata dictionary to save
    """

    # Add timestamp
    # [END]
    metadata["created_at"] = datetime.now().astimezone().isoformat()

    # Remove excluded fields
    metadata_path = metadata["metadata_path"]
    if metadata_path is None:
        raise ValueError("metadata_path must be specified (not None)")

    os.makedirs(os.path.dirname(metadata["metadata_path"]), exist_ok=True)

	# Remove excluded fields
    metadata.pop("metadata_path", None)
    metadata.pop("outdir_path", None)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Metadata saved to: {metadata_path}")


def s57_parser(s57_path, outdir_path: str = None):
    """
    Handle parsing and processing related to the S57 file.

    Args:
        s57_path (str): Path to the .000 S57 ENC file
        outdir_path (str, optional): Path to output JSON file. If None, defaults to metadata/<ENC_NAME>_metadata.json

    Returns:
        dict: Metadata including file size and other future info
    """

    if not os.path.isfile(s57_path):
        raise FileNotFoundError(f"S57 file not found: {s57_path}")

    metadata = {
    	# [1]
        "enc_name": os.path.basename(s57_path).split('.')[0],
        # [2]
        "s57_path": s57_path,
        # [3]
        "file_size_kb": get_file_size_kb(s57_path),
    }
    print(f"✅ [enc_name]: {metadata["enc_name"]}")
    print(f"✅ [s57_path]: {metadata["s57_path"]}")
    print(f"✅ [file_size_kb]: {metadata["file_size_kb"]}")


    # If no output path provided, use default
    if outdir_path is None:
        metadata["outdir_path"] = "metadata"
    else:
    	metadata["outdir_path"] = outdir_path
    print(f"✅ [outdir_path]: {metadata["outdir_path"]}")

    enc_name = metadata.get("enc_name")
    metadata_path = os.path.join(metadata["outdir_path"], f"{enc_name}_metadata.json")
    metadata["metadata_path"] = metadata_path
    print(f"✅ [metadata_path]: {metadata["metadata_path"]}")

    metadata["location_name"] = extract_named_locations(metadata["s57_path"])
    print(f"✅ [location_name]: {metadata["location_name"]}")

    # [4]
    metadata["geojson_dir"] = os.path.join(metadata["outdir_path"], "geojsons")
    os.makedirs(metadata["geojson_dir"], exist_ok=True)
    metadata["layers"] = export_geojson(metadata["s57_path"], metadata["geojson_dir"], debug = False)
    print(f"✅ [geojson_dir]: {metadata["geojson_dir"]}")
    print(f"✅ [layers]: {metadata["layers"]}")

    # [5]
    metadata["bounding_box"] = bounding_box(metadata["s57_path"], debug = False)
    print(f"✅ [bounding_box]: {metadata["bounding_box"]}")

    # [6]
    metadata["bounding_box_with_margin"] = bounding_box_padded(metadata["bounding_box"], debug = False)
    print(f"✅ [bounding_box_with_margin]: {metadata["bounding_box_with_margin"]}")

    # [7]
    metadata["center"] = bounding_box_get_center(metadata["bounding_box"])
    print(f"✅ [center]: {metadata["center"]}")

    # [8]
    metadata["zoom_range"] = bounding_box_zoom_range()
    print(f"✅ [zoom_range]: {metadata["zoom_range"]}")

    # [9]
    metadata["tile_dir"] = os.path.join(metadata["outdir_path"], "tiles")
    # Add download TILE here
    # def download_bbox_tiles(bounding_box: dict, zoom_range: dict, tile_dir: str, user_agent: str = None, max_workers: int, debug: bool = False) -> int:
    metadata["tile_count"] = download_bbox_tiles(
    									bounding_box = metadata["bounding_box_with_margin"],
    									zoom_range = metadata["zoom_range"],
    									tile_dir = metadata["tile_dir"],
    									user_agent = USER_AGENT,
    									max_workers = 10, debug = False)
    metadata["tile_dir_size_kb"] = get_dir_size_kb(metadata["tile_dir"])
    print(f"✅ [tile_dir]: {metadata["tile_dir"]}")
    print(f"✅ [tile_count]: {metadata["tile_count"]}")
    print(f"✅ [tile_dir_size_kb]: {metadata["tile_dir_size_kb"]}")
    return metadata

def main():
    parser = argparse.ArgumentParser(description="Parse S57 ENC and tile directory metadata.")
    parser.add_argument("-s", "--s57-file", dest="s57_file", required=True, help="Path to the S57 .000 file")
    parser.add_argument("-o", "--outdir", dest="outdir", required=False, help="Path to the all metadata from S57 .000 file")

    args = parser.parse_args()

    try:
        s57_meta = s57_parser(args.s57_file, args.outdir)

        metadata_save(s57_meta)

    except FileNotFoundError as e:
        print("Error:", e)
        return

if __name__ == "__main__":
    main()
