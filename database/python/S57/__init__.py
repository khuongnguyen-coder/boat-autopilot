# S57/__init__.py

"""
S57 package initializer.

This module exposes core utility functions for working with S57 ENC data.
Users can import from `S57` directly to access key functionality such as
GeoJSON export and bounding box utilities.
"""

# Export function to convert S57 ENC layers to GeoJSON
from .export_geojson import export_geojson

# Bounding box utilities
from .bounding_box import (
    bounding_box,               # Extract the largest bounding box from S57 layers
    bounding_box_padded,        # Add margin to the bounding box
    bounding_box_get_center,    # Calculate the center point of a bounding box
    bounding_box_zoom_range     # Placeholder: determine suitable zoom level range
)

# Define the public API of the S57 package
__all__ = [
    "export_geojson",
    "bounding_box",
    "bounding_box_padded",
    "bounding_box_get_center",
    "bounding_box_zoom_range"
]
