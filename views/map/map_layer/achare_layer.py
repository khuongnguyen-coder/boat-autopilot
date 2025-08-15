import json
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk

from views.map.map_layer.geojson_layer import GeoJSONLayer

class ACHARELayer(GeoJSONLayer):
    def __init__(self, filepath, line_color=(1.0, 0, 0), line_width=2, fill_color=(1.0, 1.0, 0), fill_opacity=0.3):
        super().__init__(
            filepath=filepath,
            title="Anchorage Area",
            line_color=line_color,
            line_width=line_width,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            layer_id="ACHARE"
        )

    def properties_str(self, props):
        important_keys = ["OBJNAM", "INFORM", "CATACH"]
        lines = []
        
        # First important keys
        for key in important_keys:
            if key in props:
                value = props[key]
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                lines.append(f"{key}: {value}")
        
        # Then the rest
        for key, value in props.items():
            if key not in important_keys:
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)

    def render(self, ctx, map_obj):
        """Render with base behavior, but store info for hit detection."""
        super().render(ctx, map_obj)
        # Optional: could add text labels, markers, or store clickable regions here.