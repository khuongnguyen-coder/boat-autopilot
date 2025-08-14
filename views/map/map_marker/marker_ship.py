import math
from gi.repository import GdkPixbuf, Gdk

class MapMarkerShip:
    def __init__(self, image_path, size=24, name="My Ship"):
        self.original_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_path, size, size)
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
        """Draw the ship marker with smooth rotation."""
        if center:
            px -= self.original_pixbuf.get_width() / 2
            py -= self.original_pixbuf.get_height() / 2

        # Store bounds for hit detection
        self.last_draw_bounds = (px, py,
                                 self.original_pixbuf.get_width(),
                                 self.original_pixbuf.get_height())

        ctx.save()

        # Translate to ship center for rotation
        cx = px + self.original_pixbuf.get_width() / 2
        cy = py + self.original_pixbuf.get_height() / 2
        ctx.translate(cx, cy)

        # Rotate counterclockwise for Cairo (negative for clockwise heading)
        ctx.rotate(math.radians(-self.heading))

        # Draw with top-left corner adjusted after rotation
        Gdk.cairo_set_source_pixbuf(ctx, self.original_pixbuf,
                                    -self.original_pixbuf.get_width() / 2,
                                    -self.original_pixbuf.get_height() / 2)
        ctx.paint()

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