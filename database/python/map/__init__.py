# map/__init__.py

"""
map package initializer
=======================

This module exposes core mapping utilities for convenient access when
importing from the `map` package directly.

Included utilities:
- `download_bbox_tiles`: Download raster tiles for a given bounding box
- `export_geojson`: Export features as GeoJSON (imported for side effects or internal use)
"""

# Import core functionality from submodules
from .raster_tile_download import (
    download_bbox_tiles,  # Download raster tiles within a bounding box
)

# Define the public API of the map package
__all__ = [
    "download_bbox_tiles",
]
