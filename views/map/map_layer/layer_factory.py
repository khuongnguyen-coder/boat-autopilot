"""
layer_factory.py

This module defines a central registry (LAYER_CLASS_MAP) that maps ENC layer IDs
(e.g., "ACHARE", "ACHBRT", "AIRARE") to their corresponding layer classes and
styling options.

Purpose:
    - Acts as a factory for creating styled layer instances.
    - Keeps styling consistent across the application.
    - Makes it easy to add new ENC layers by simply extending this map.

Each entry in LAYER_CLASS_MAP specifies:
    - "class":       The Python class used to render this ENC layer.
    - "line_color":  RGB stroke color (0-1 range).
    - "width":       Stroke width in pixels.
    - "fill_color":  RGB fill color (0-1 range) for polygons.
    - "fill_opacity":Transparency for fill (0.0 = fully transparent, 1.0 = opaque).
    - "line_style":  A Cairo dash pattern list, imported from LINE_STYLE_PATTERNS,
                     which defines the stroke style (solid, dashed, dotted, etc.).

Example LINE_STYLE_PATTERNS from style_constants.py:
    "solid":  []              → continuous solid line
    "dashed": [10.0, 5.0]     → 10px dash, 5px gap
    "dotted": [2.0, 4.0]      → 2px dot, 4px gap

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

from views.map.map_layer.style_constants import LINE_STYLE_PATTERNS
from views.map.map_layer.achare_layer import ACHARELayer
from views.map.map_layer.achbrt_layer import ACHBRTLayer
from views.map.map_layer.airare_layer import AIRARELayer

# -----------------------------------------------------------------------------
# LAYER_CLASS_MAP
#
# Main dictionary for mapping ENC layer codes to their classes + styling.
# -----------------------------------------------------------------------------
LAYER_CLASS_MAP = {
    "ACHARE": {
        "class": ACHARELayer,
        "line_color": (0.0, 0.0, 0.5),              # Dark blue stroke
        "width": 1,
        "fill_color": (0.5, 1.0, 1.0),              # Light cyan fill
        "fill_opacity": 0.1,                        # Semi-transparent
        "line_style": LINE_STYLE_PATTERNS["solid"]  # Solid line style
    },

    "ACHBRT": {
        "class": ACHBRTLayer,
        "line_color": (0.0, 0.0, 0.5),              # Dark blue for depth contour lines
        "width": 1,
        "fill_color": (0.7, 0.85, 1.0),             # Light blue for shallow water areas
        "fill_opacity": 0.3,                        # Semi-transparent
        "line_style": LINE_STYLE_PATTERNS["solid"]  # Solid line style
    },

    "AIRARE": {
        "class": AIRARELayer,
        "line_color": (1.0, 0.0, 0.0),              # Red boundary lines for restricted airspace
        "width": 1,
        "fill_color": (1.0, 0.8, 0.8),              # Light red/pink fill
        "fill_opacity": 0.3,                        # Semi-transparent
        "line_style": LINE_STYLE_PATTERNS["solid"]  # Solid line style
    }
}
