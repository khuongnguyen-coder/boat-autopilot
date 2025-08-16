"""
map_marker_ship.py - Ship marker overlay for map visualization in VNEST Autopilot.

This module defines the `MapMarkerShip` class, which is responsible for:
    - Displaying a ship marker (with rotation and label) on the map.
    - Managing ship attributes (location, heading, visibility, name).
    - Providing hit detection for user interaction (e.g., click on ship).
    - Returning ship information as dict/string for debugging or display.

Usage:
    from views.map.map_marker_ship import MapMarkerShip

    ship = MapMarkerShip("assets/ship.png", size=32, name="Vessel A")
    ship.set_location(10.762622, 106.660172)  # Lat/Lon
    ship.set_heading(45)  # NE
    ship.draw(ctx, px, py)  # Cairo context with map coordinates

Dependencies:
    - GTK (GdkPixbuf for image loading, Cairo for drawing).

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import math
import gi
import cairo
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf


class MapMarkerShip:
    """
    Ship marker that can be drawn on the map with rotation and label.

    Attributes:
        pixbuf (GdkPixbuf.Pixbuf): The ship image loaded as a pixbuf.
        lat (float): Latitude of the ship in decimal degrees.
        lon (float): Longitude of the ship in decimal degrees.
        heading (float): Heading in degrees (0° = north, clockwise).
        visible (bool): Whether the marker should be drawn.
        name (str): Ship name displayed above the marker.
        last_draw_bounds (tuple): Pixel bounds (x, y, w, h) of last draw 
                                  for hit detection.
    """

    def __init__(self, image_path, size=24, name="My Ship"):
        """
        Initialize a ship marker.

        Args:
            image_path (str): Path to the ship icon image.
            size (int): Pixel size of the marker image. Default = 24 px.
            name (str): Ship display name. Default = "My Ship".
        """
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_path, size, size)
        self.lat = 0.0
        self.lon = 0.0
        self.heading = 0  # 0° = north
        self.visible = True
        self.name = name
        self.last_draw_bounds = None  # (x, y, w, h) in pixels

    def set_location(self, lat, lon):
        """Set the latitude and longitude of the ship."""
        self.lat = lat
        self.lon = lon

    def set_heading(self, heading_deg):
        """Set ship heading in degrees (0° = north, clockwise)."""
        self.heading = heading_deg % 360

    def draw(self, ctx, px, py, center=True):
        """
        Draw the ship marker with smooth rotation and a label above it.

        Args:
            ctx (cairo.Context): Cairo drawing context.
            px (float): X position in pixels.
            py (float): Y position in pixels.
            center (bool): Whether to center the marker on (px, py).
        """
        if self.pixbuf is None:
            return

        if center:
            px -= self.pixbuf.get_width() / 2
            py -= self.pixbuf.get_height() / 2

        # Store bounds for hit detection
        self.last_draw_bounds = (px, py,
                                 self.pixbuf.get_width(),
                                 self.pixbuf.get_height())

        # --- Draw the ship pixbuf with rotation ---
        ctx.save()
        cx = px + self.pixbuf.get_width() / 2
        cy = py + self.pixbuf.get_height() / 2
        ctx.translate(cx, cy)
        ctx.rotate(math.radians(-self.heading))
        Gdk.cairo_set_source_pixbuf(ctx, self.pixbuf,
                                    -self.pixbuf.get_width() / 2,
                                    -self.pixbuf.get_height() / 2)
        ctx.paint()
        ctx.restore()

        # --- Draw the ship name above the pixbuf ---
        if self.name:
            ctx.save()
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(12)
            ctx.set_source_rgb(0, 0, 0)  # black color
            text_extents = ctx.text_extents(self.name)
            text_x = cx - text_extents.width / 2
            text_y = cy - self.pixbuf.get_height() / 2 - 5  # 5px above the pixbuf
            ctx.move_to(text_x, text_y)
            ctx.show_text(self.name)
            ctx.restore()

    def hit_test(self, click_x, click_y):
        """
        Check if a click is inside the marker bounds.
        Note: Rotation is ignored for simplicity.

        Args:
            click_x (float): X position of click.
            click_y (float): Y position of click.

        Returns:
            bool: True if inside marker bounds, False otherwise.
        """
        if not self.last_draw_bounds:
            return False
        px, py, w, h = self.last_draw_bounds
        return px <= click_x <= px + w and py <= click_y <= py + h
    
    def get_info_dict(self):
        """
        Get ship info as a dictionary.

        Returns:
            dict: { "name", "lat", "lon", "heading" }
        """
        return {
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "heading": self.heading
        }

    def get_info_str(self):
        """
        Get ship info as a human-readable string.

        Returns:
            str: Multi-line text summary of ship details.
        """
        return (
            f"{self.name}\n"
            f"Lat: {self.lat:.6f}\n"
            f"Lon: {self.lon:.6f}\n"
            f"Heading: {self.heading:.1f}"
        )
