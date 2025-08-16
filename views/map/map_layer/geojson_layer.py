"""
geojson_layer.py

Base class for rendering GeoJSON layers on the map using Cairo + GTK.

Responsibilities:
    - Load and store features from a GeoJSON file.
    - Render polygons, multipolygons, and linestrings with stroke/fill styles.
    - Support customizable line color, fill color, opacity, and dash patterns.
    - Perform hit-testing on rendered geometries for user interaction.

Dependencies:
    - Uses LINE_STYLE_PATTERNS from style_constants.py for predefined dash styles.
    - Relies on map_obj.latlon_to_pixels() for coordinate projection.

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import json
import math
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk

from views.map.map_layer.style_constants import LINE_STYLE_PATTERNS

class GeoJSONLayer:
    # =========================================================================
    # Initialization
    # =========================================================================
    def __init__(
        self,
        filepath,
        title=None,
        line_color=(0, 0, 0),
        line_width=1,
        fill_color=None,
        fill_opacity=0.3,
        line_style=None,
        layer_id=None
    ):
        """
        Initialize a GeoJSON layer for rendering on the map.

        Args:
            filepath (str): Path to the GeoJSON file.
            line_color (tuple): Stroke color as RGB (0-1), default dark blue.
            line_width (int/float): Stroke width in pixels.
            fill_color (tuple): Fill color as RGB (0-1), default light blue.
            fill_opacity (float): Fill transparency (0.0 = transparent, 1.0 = opaque).
            line_style (list, optional): Cairo dash pattern (from LINE_STYLE_PATTERNS). Defaults to solid line if None.
        """
        # Metadata and styling
        self.layer_id = layer_id
        self.filepath = filepath
        self.title = title or filepath
        self.line_color = line_color
        self.line_width = line_width
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity

        # Store the actual dash pattern (list), not a string
        self.line_style = line_style if line_style is not None else LINE_STYLE_PATTERNS["solid"]

        # Storage for name, crs, features loaded from the GeoJSON file
        self.name = None
        self.crs = None # crs = crs => properties => name
        self.features = []

        # Load geometry and properties from file
        self.load_geojson(filepath)

    # =========================================================================
    # Data loading
    # =========================================================================
    def load_geojson(self, filepath):
        """Load features from the given GeoJSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Store collection name if present
        self.name = data.get("name", None)

        # Store features list
        self.features = data.get("features", [])

        # Store CRS if present
        crs_obj = data.get("crs", {})
        self.crs = None
        if isinstance(crs_obj, dict):
            props = crs_obj.get("properties", {})
            if isinstance(props, dict):
                self.crs = props.get("name", None)

    def get_properties(self, feature):
        """Return the properties dictionary from a GeoJSON feature."""
        return feature.get("properties", {})

    # =========================================================================
    # Rendering
    # =========================================================================
    def draw(self, ctx, map_obj):
        """Entry point for MapVisualize to render this layer."""
        self.render(ctx, map_obj)

    def render(self, ctx, map_obj):
        """
        Render this GeoJSON layer using Cairo context `ctx`
        and a map projection object (`map_obj`).
        """
        ctx.set_line_width(self.line_width)

        for feature in self.features:
            geometry = feature.get("geometry", {})
            geom_type = geometry.get("type")
            coords = geometry.get("coordinates")

            if geom_type == "LineString":
                ctx.set_source_rgb(*self.line_color)
                self._draw_linestring(ctx, coords, map_obj)
                self._apply_line_style(ctx)
                self._draw_label(ctx, self.name)
                ctx.stroke()

            elif geom_type == "Polygon":
                for ring in coords:
                    if self.fill_color:
                        self._draw_linestring(ctx, ring, map_obj)
                        ctx.close_path()
                        ctx.set_source_rgba(
                            self.fill_color[0], self.fill_color[1], self.fill_color[2], self.fill_opacity
                        )
                        ctx.fill_preserve()
                    ctx.set_source_rgb(*self.line_color)
                    self._apply_line_style(ctx)
                    self._draw_label(ctx, self.name)
                    ctx.stroke()

            elif geom_type == "MultiPolygon":
                for polygon in coords:
                    for ring in polygon:
                        if self.fill_color:
                            self._draw_linestring(ctx, ring, map_obj)
                            ctx.close_path()
                            ctx.set_source_rgba(
                                self.fill_color[0], self.fill_color[1], self.fill_color[2], self.fill_opacity
                            )
                            ctx.fill_preserve()
                        ctx.set_source_rgb(*self.line_color)
                        self._apply_line_style(ctx)
                        self._draw_label(ctx, self.name)
                        ctx.stroke()

    def _draw_linestring(self, ctx, coords, map_obj):
        """Draw a LineString or polygon ring path (without stroking/filling)."""
        for i, (lon, lat) in enumerate(coords):
            x, y = map_obj.latlon_to_pixels(lat, lon)
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
    
    def _draw_label(self, ctx, label_str):
        ctx.show_text(label_str)

    def _apply_line_style(self, ctx):
        """
        Apply line style before stroking.

        Uses predefined dash patterns from LINE_STYLE_PATTERNS.
        Example:
            []            → solid
            [10.0, 5.0]   → dashed
            [2.0, 4.0]    → dotted
        """
        ctx.set_dash(self.line_style)

    # =========================================================================
    # Hit-testing
    # =========================================================================
    def hit_test(self, px, py, map_obj, tolerance=5):
        """
        Return the first feature hit by the given pixel coords, or None.

        For lines: checks if click is within `tolerance` pixels of any segment.
        For polygons: checks against boundary rings.
        """
        for feature in self.features:
            geometry = feature.get("geometry", {})
            geom_type = geometry.get("type")
            coords = geometry.get("coordinates")

            if geom_type == "LineString":
                if self._line_hit_test(coords, px, py, map_obj, tolerance):
                    return feature
            elif geom_type == "Polygon":
                for ring in coords:
                    if self._line_hit_test(ring, px, py, map_obj, tolerance):
                        return feature
            elif geom_type == "MultiPolygon":
                for polygon in coords:
                    for ring in polygon:
                        if self._line_hit_test(ring, px, py, map_obj, tolerance):
                            return feature
        return None

    def _line_hit_test(self, coords, px, py, map_obj, tolerance):
        """Check if point (px, py) is near any line segment in coords."""
        points = [map_obj.latlon_to_pixels(lat, lon) for lon, lat in coords]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if self._point_to_segment_dist(px, py, x1, y1, x2, y2) <= tolerance:
                return True
        return False

    def _point_to_segment_dist(self, px, py, x1, y1, x2, y2):
        """
        Compute the minimum distance from a point to a line segment.

        Returns:
            float: distance in pixels.
        """
        dx = x2 - x1
        dy = y2 - y1
        if dx == dy == 0:  # degenerate segment (point)
            return math.hypot(px - x1, py - y1)

        # Project point onto segment, clamped between [0, 1]
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy

        return math.hypot(px - proj_x, py - proj_y)
