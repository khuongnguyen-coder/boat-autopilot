from dataclasses import dataclass
from typing import List

@dataclass
class BoundingBox:
    minx: float
    miny: float
    maxx: float
    maxy: float

@dataclass
class Center:
    lon: float
    lat: float

@dataclass
class ZoomRange:
    min: int
    max: int

@dataclass
class EncMetadata:
    enc_name: str
    s57_path: str
    file_size_kb: float
    location_name: List[str]
    geojson_dir: str
    layers: List[str]
    bounding_box: BoundingBox
    bounding_box_with_margin: BoundingBox
    center: Center
    zoom_range: ZoomRange
    tile_dir: str
    tile_count: int
    tile_dir_size_kb: float
    created_at: str  # You can parse this to datetime if needed

