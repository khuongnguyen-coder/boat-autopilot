import math
import gi
import cairo
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

class MapMarkerShip:
    def __init__(self, image_path, size=24, name="My Ship"):
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_path, size, size)
        self.lat = 0.0
        self.lon = 0.0
        self.heading = 0  # 0° = north
        self.visible = True
        self.name = name
        self.last_draw_bounds = None  # (x, y, w, h) in pixels

    def set_location(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def set_heading(self, heading_deg):
        """Set heading in degrees (0° = north, clockwise)."""
        self.heading = heading_deg % 360

    def draw(self, ctx, px, py, center=True):
        """Draw the ship marker with smooth rotation and a label above it."""

        if self.pixbuf is None:
            return

        if center:
            px -= self.pixbuf.get_width() / 2
            py -= self.pixbuf.get_height() / 2

        # Store bounds for hit detection
        self.last_draw_bounds = (px, py,
                                self.pixbuf.get_width(),
                                self.pixbuf.get_height())

        # Draw the pixbuf with rotation
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

        # Draw the ship name above the pixbuf
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
        """Check if click is inside marker bounds (no rotation check for simplicity)."""
        if not self.last_draw_bounds:
            return False
        px, py, w, h = self.last_draw_bounds
        return px <= click_x <= px + w and py <= click_y <= py + h
    
    def get_info_dict(self):
        return {
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "heading": self.heading
        }

    def get_info_str(self):
        return (
            f"{self.name}\n"
            f"Lat: {self.lat:.6f}\n"
            f"Lon: {self.lon:.6f}\n"
            f"Heading: {self.heading:.1f}"
        )
