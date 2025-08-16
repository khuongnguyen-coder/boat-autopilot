"""
metadata_models.py - Data models for ENC (Electronic Navigational Chart) metadata.

This module defines structured dataclasses that are used throughout the
VNEST Autopilot application for managing ENC datasets, tile information,
and associated geospatial metadata.

Features:
    - BoundingBox:  Geographic extent of ENC data
    - Center:       Map center coordinates
    - ZoomRange:    Min/max zoom levels for map display
    - EncMetadata:  Comprehensive ENC dataset metadata container

Usage:
    from metadata_models import EncMetadata, BoundingBox, Center, ZoomRange

    bbox = BoundingBox(minx=10, miny=20, maxx=30, maxy=40)
    center = Center(lon=15.0, lat=25.0)
    zoom = ZoomRange(min=5, max=12)

    enc = EncMetadata(
        enc_name="VN123",
        s57_path="/data/charts/VN123.000",
        file_size_kb=1200.5,
        location_name=["Hai Phong", "Cat Ba"],
        geojson_dir="geojson/vn123",
        layers=["ACHARE", "ACHBRT", "DEPCNT"],
        bounding_box=bbox,
        bounding_box_with_margin=bbox,
        center=center,
        zoom_range=zoom,
        tile_dir="tiles/vn123",
        tile_count=3456,
        tile_dir_size_kb=45000.0,
        created_at="2025-08-16T21:00:00Z"
    )
"""

from dataclasses import dataclass
from typing import List


# ********************************************************************************************
@dataclass
class BoundingBox:
    """
    Geographic bounding box for ENC data.

    Attributes:
        minx (float): Minimum longitude (west).
        miny (float): Minimum latitude (south).
        maxx (float): Maximum longitude (east).
        maxy (float): Maximum latitude (north).
    """
    minx: float
    miny: float
    maxx: float
    maxy: float
# ********************************************************************************************


# ********************************************************************************************
@dataclass
class Center:
    """
    Geographic center point of ENC data.

    Attributes:
        lon (float): Longitude of center.
        lat (float): Latitude of center.
    """
    lon: float
    lat: float
# ********************************************************************************************


# ********************************************************************************************
@dataclass
class ZoomRange:
    """
    Zoom level range supported for ENC tile display.

    Attributes:
        min (int): Minimum zoom level.
        max (int): Maximum zoom level.
    """
    min: int
    max: int
# ********************************************************************************************


# ********************************************************************************************
@dataclass
class EncMetadata:
    """
    Comprehensive metadata structure for an ENC dataset.

    Attributes:
        enc_name (str): Identifier of the ENC chart.
        s57_path (str): Absolute path to the S57 ENC file.
        file_size_kb (float): File size of the S57 file in KB.
        location_name (List[str]): Human-readable location names.
        geojson_dir (str): Directory path containing derived GeoJSON files.
        layers (List[str]): List of available map layers in this ENC.
        bounding_box (BoundingBox): Raw bounding box of ENC data.
        bounding_box_with_margin (BoundingBox): Bounding box with margin applied.
        center (Center): Center coordinate for map display.
        zoom_range (ZoomRange): Min/max zoom levels supported.
        tile_dir (str): Directory path for pre-rendered tiles.
        tile_count (int): Number of tiles generated.
        tile_dir_size_kb (float): Disk usage of the tile directory in KB.
        created_at (str): Creation timestamp (ISO8601 format).
    
    Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
    """
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
# ********************************************************************************************
