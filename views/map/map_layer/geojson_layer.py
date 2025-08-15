import json
import math
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk

class GeoJSONLayer:
    def __init__(self, filepath, title=None, line_color=(0, 0, 0), line_width=2, fill_color=None, fill_opacity=0.3):
        """
        Base class to load and render GeoJSON layers.

        :param filepath: Path to .geojson file
        :param title: Human-readable title
        :param line_color: RGB tuple (0-1 range)
        :param line_width: Stroke width in pixels
        """
        self.filepath = filepath
        self.title = title or filepath
        self.line_color = line_color
        self.line_width = line_width
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.features = []
        self.load_geojson(filepath)

    def load_geojson(self, filepath):
        """Load features from the given GeoJSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.features = data.get("features", [])

    def get_properties(self, feature):
        """Return properties dict from a feature."""
        return feature.get("properties", {})

    # ****************************************************************************************
    # [Render / draw method]
    def draw(self, ctx, map_obj):
        """Entry point for MapVisualize to render this layer."""
        self.render(ctx, map_obj)

    def render(self, ctx, map_obj):
        """
        Render this GeoJSON layer using Cairo context `ctx` and a map projection object.
        """
        ctx.set_line_width(self.line_width)

        for feature in self.features:
            geometry = feature.get("geometry", {})
            geom_type = geometry.get("type")
            coords = geometry.get("coordinates")

            if geom_type == "LineString":
                ctx.set_source_rgb(*self.line_color)
                self._draw_linestring(ctx, coords, map_obj)
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
                        ctx.stroke()

    def _draw_linestring(self, ctx, coords, map_obj):
        """Draw a LineString or polygon ring path (no stroke/fill)."""
        for i, (lon, lat) in enumerate(coords):
            x, y = map_obj.lonlat_to_pixels(lon, lat)
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
    # ****************************************************************************************

    # ****************************************************************************************
    # [Hit test]
    def hit_test(self, px, py, map_obj, tolerance=5):
        """
        Return the first feature hit by the given pixel coords, or None.
        For lines: checks if click is within `tolerance` pixels of any segment.
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
        """Check if point is near any line segment in coords."""
        points = [map_obj.lonlat_to_pixels(lon, lat) for lon, lat in coords]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if self._point_to_segment_dist(px, py, x1, y1, x2, y2) <= tolerance:
                return True
        return False

    def _point_to_segment_dist(self, px, py, x1, y1, x2, y2):
        """Distance from point to segment."""
        dx = x2 - x1
        dy = y2 - y1
        if dx == dy == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)
    # ****************************************************************************************