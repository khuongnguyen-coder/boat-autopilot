"""
airare_layer.py

Defines AIRARELayer, a specialized GeoJSONLayer for rendering
Airspace Areas (AIRARE) from ENC GeoJSON data.

Features:
    - Preconfigured defaults for airspace area styling.
    - Supports line color, fill color, fill opacity, and line style.
    - Provides a formatted string representation of feature properties.

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import json
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk

from views.map.map_layer.geojson_layer import GeoJSONLayer


class AIRARELayer(GeoJSONLayer):
    # =========================================================================
    # Initialization
    # =========================================================================
    def __init__(
        self,
        filepath,
        line_color=(1.0, 0, 0),
        line_width=1,
        fill_color=(1.0, 0.8, 0.8),
        fill_opacity=0.3,
        line_style=None,
        layer_id="AIRARE"
    ):
        """
        Initialize an AIRARE (Airspace Areas) layer.

        Args:
            filepath (str): Path to the GeoJSON file.
            line_color (tuple): Stroke color as RGB (0-1), default dark blue.
            line_width (int/float): Stroke width in pixels.
            fill_color (tuple): Fill color as RGB (0-1), default light blue.
            fill_opacity (float): Fill transparency (0.0 = transparent, 1.0 = opaque).
            line_style (list, optional): Cairo dash pattern (from LINE_STYLE_PATTERNS). Defaults to solid line if None.
            layer_id: Unique ENC identifier, default AIRARE
        """
        super().__init__(
            filepath=filepath,
            title="Airspace Area",        # Human-readable name
            line_color=line_color,        # Stroke color
            line_width=line_width,        # Stroke width
            fill_color=fill_color,        # Polygon fill color
            fill_opacity=fill_opacity,    # Fill transparency
            line_style=line_style,        # Pass None → solid, or custom pattern
            layer_id=layer_id             # Unique ENC identifier
        )

    # =========================================================================
    # Properties Formatting
    # =========================================================================
    def properties_str(self, props):
        """
        Return a formatted string of feature properties.

        Important keys are shown first, followed by the rest.
        """
        important_keys = ["OBJNAM", "AIRACN", "AIRSTA", "CATARA", "FLTOPA", "FLBOT"]
        lines = []
        
        # First, show important keys
        for key in important_keys:
            if key in props:
                value = props[key]
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                lines.append(f"{key}: {value}")
        
        # Then, show all other keys
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
        Render with base behavior, but can be extended.

        Currently:
            - Calls base GeoJSONLayer.render().
            - Can be extended to add:
                • Text labels
                • Markers
                • Clickable or interactive regions
        """
        super().render(ctx, map_obj)
