"""
achare_layer.py

Defines ACHARELayer, a specialized GeoJSONLayer for rendering
Anchorage Areas (ACHARE) from ENC GeoJSON data.

Features:
    - Preconfigured defaults for Anchorage Area styling.
    - Supports line color, fill color, fill opacity, and dash style.
    - Formats feature properties for display in tooltips or inspection.

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import json
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk

from views.map.map_layer.geojson_layer import GeoJSONLayer


class ACHARELayer(GeoJSONLayer):
    # =========================================================================
    # Initialization
    # =========================================================================
    def __init__(
        self,
        filepath,
        line_color=(1.0, 0, 0),
        line_width=2,
        fill_color=(1.0, 1.0, 0),
        fill_opacity=0.3,
        line_style=None
    ):
        """
        Initialize the ACHARE (Anchorage Area) layer.

        Args:
            filepath (str): Path to the GeoJSON file.
            line_color (tuple): Stroke color as RGB (0-1), default dark blue.
            line_width (int/float): Stroke width in pixels.
            fill_color (tuple): Fill color as RGB (0-1), default light blue.
            fill_opacity (float): Fill transparency (0.0 = transparent, 1.0 = opaque).
            line_style (list, optional): Cairo dash pattern (from LINE_STYLE_PATTERNS). Defaults to solid line if None.
        """
        super().__init__(
            filepath=filepath,
            title="Anchorage Area",       # Human-readable name
            line_color=line_color,        # Stroke color
            line_width=line_width,        # Stroke width
            fill_color=fill_color,        # Polygon fill color
            fill_opacity=fill_opacity,    # Fill transparency
            line_style=line_style,        # Pass None → solid, or custom pattern
            layer_id="ACHARE"             # Unique ENC identifier
        )

    # =========================================================================
    # Properties Formatting
    # =========================================================================
    def properties_str(self, props):
        """
        Format a feature's properties into a human-readable string.

        Important keys are displayed first, then all remaining keys.
        """
        important_keys = ["OBJNAM", "INFORM", "CATACH"]
        lines = []

        # First, show important keys
        for key in important_keys:
            if key in props:
                value = props[key]
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                lines.append(f"{key}: {value}")

        # Then, show all other properties
        for key, value in props.items():
            if key not in important_keys:
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    # =========================================================================
    # Rendering
    # =========================================================================
    def render(self, ctx, map_obj):
        """
        Render this ACHARE layer on the map.

        Currently:
            - Uses GeoJSONLayer.render() to draw polygons/lines with styles.
            - Can be extended to add:
                * Feature labels
                * Symbols/icons
                * Interactive hit regions
        """
        super().render(ctx, map_obj)
