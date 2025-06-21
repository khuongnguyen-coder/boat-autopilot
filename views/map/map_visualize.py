import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

import threading
from gi.repository import GLib

import math
import os
import urllib.request

from utils.path import utils_path_get_asset

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

TILE_SIZE = 256
ZOOM = 16

class MapVisualize(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        LOG_DEBUG("MapVisualize init started")

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_can_focus(True)
        self.set_focus_on_click(True)
        self.set_app_paintable(True)

        # Enable event masks
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.STRUCTURE_MASK |
            Gdk.EventMask.EXPOSURE_MASK
        )

        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_button_press)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("button-release-event", self.on_button_release)

        # self.set_size_request(800, 600)

        self.center_lat = 10.8382543
        self.center_lon = 106.8317088
        self.zoom = ZOOM
        self.offset_x = 0
        self.offset_y = 0
        self.tiles = {}

        self.clicked_latlon = None

        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        marker_path = utils_path_get_asset("map", "marker.png")
        self.marker_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(marker_path, 24, 24)
        
        LOG_DEBUG("MapVisualize init done")

    def on_button_press(self, widget, event):
        LOG_DEBUG(f"on_button_press: {event.x}, {event.y}, button={event.button}")
        
        # Only respond to left mouse button (button 1)
        if event.button != 1:
            return False  # Ignore other buttons

        # Handle left-click: begin drag and register as click
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.start_offset_x = self.offset_x
        self.start_offset_y = self.offset_y

        # Also treat this as a click for coordinate detection
        self.on_map_clicked(event.x, event.y)

        return True

    def on_scroll(self, widget, event):
        old_zoom = self.zoom

        if event.direction == Gdk.ScrollDirection.UP:
            self.zoom = min(self.zoom + 1, 19)  # limit zoom max
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.zoom = max(self.zoom - 1, 1)   # limit zoom min
        else:
            return False

        LOG_DEBUG(f"Zoom changed: {old_zoom} → {self.zoom}")

        self.tiles.clear()  # clear cached tiles to reload
        self.queue_draw()
        return True

    def on_motion_notify(self, widget, event):
        if self.dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.offset_x = self.start_offset_x + dx
            self.offset_y = self.start_offset_y + dy
            self.queue_draw()
        return True

    def on_button_release(self, widget, event):
        if event.button == 1 and self.dragging:
            self.dragging = False
            dx = -self.offset_x / TILE_SIZE
            dy = -self.offset_y / TILE_SIZE
            cx, cy = self.deg2num(self.center_lat, self.center_lon, self.zoom)
            new_cx = cx + dx
            new_cy = cy + dy
            self.center_lat, self.center_lon = self.num2deg(new_cx, new_cy, self.zoom)
            self.offset_x = 0
            self.offset_y = 0
            self.queue_draw()
        return True

    def on_map_clicked(self, x, y):
        LOG_DEBUG(f"on_map_clicked: {x}, {y}")
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        center_xtile, center_ytile = self.deg2num(self.center_lat, self.center_lon, self.zoom)

        tiles_x = math.ceil(width / TILE_SIZE) + 2
        tiles_y = math.ceil(height / TILE_SIZE) + 2

        start_xtile = int(center_xtile - tiles_x // 2)
        start_ytile = int(center_ytile - tiles_y // 2)

        offset_x = -((center_xtile - int(center_xtile)) * TILE_SIZE) + self.offset_x
        offset_y = -((center_ytile - int(center_ytile)) * TILE_SIZE) + self.offset_y

        clicked_xtile = (x - offset_x) / TILE_SIZE + start_xtile
        clicked_ytile = (y - offset_y) / TILE_SIZE + start_ytile

        lat, lon = self.num2deg(clicked_xtile, clicked_ytile, self.zoom)
        self.clicked_latlon = (lat, lon)
        LOG_DEBUG(f"Clicked at pixel ({x:.0f}, {y:.0f}) => Coordinates: ({lat:.6f}, {lon:.6f})")
        self.queue_draw()

    def on_draw(self, widget, ctx):
        # LOG_DEBUG("on_draw called")
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        center_x, center_y = self.deg2num(self.center_lat, self.center_lon, self.zoom)
        tiles_x = math.ceil(width / TILE_SIZE) + 2
        tiles_y = math.ceil(height / TILE_SIZE) + 2
        start_x = int(center_x - tiles_x // 2)
        start_y = int(center_y - tiles_y // 2)
        offset_x = -((center_x - int(center_x)) * TILE_SIZE) + self.offset_x
        offset_y = -((center_y - int(center_y)) * TILE_SIZE) + self.offset_y

        for i in range(tiles_x):
            for j in range(tiles_y):
                x = start_x + i
                y = start_y + j
                tile_path = self.download_tile(x, y, self.zoom)
                if tile_path:
                    try:
                        key = f"{self.zoom}/{x}/{y}"
                        if key not in self.tiles:
                            self.tiles[key] = GdkPixbuf.Pixbuf.new_from_file(tile_path)
                        pixbuf = self.tiles[key]
                        draw_x = round(i * TILE_SIZE + offset_x)
                        draw_y = round(j * TILE_SIZE + offset_y)
                        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, draw_x, draw_y)
                        ctx.paint()
                    except Exception as e:
                        LOG_ERR(f"Error drawing tile {x},{y}: {e}")

        # Draw marker
        center_xtile, center_ytile = self.deg2num(self.center_lat, self.center_lon, self.zoom)
        pixel_x = round((center_xtile - start_x) * TILE_SIZE + offset_x - self.marker_pixbuf.get_width() / 2)
        pixel_y = round((center_ytile - start_y) * TILE_SIZE + offset_y - self.marker_pixbuf.get_height())
        Gdk.cairo_set_source_pixbuf(ctx, self.marker_pixbuf, pixel_x, pixel_y)
        ctx.paint()

        # Clicked marker
        if self.clicked_latlon:
            lat, lon = self.clicked_latlon
            xtile, ytile = self.deg2num(lat, lon, self.zoom)
            px = round((xtile - start_x) * TILE_SIZE + offset_x - self.marker_pixbuf.get_width() / 2)
            py = round((ytile - start_y) * TILE_SIZE + offset_y - self.marker_pixbuf.get_height())
            Gdk.cairo_set_source_pixbuf(ctx, self.marker_pixbuf, px, py)
            ctx.paint()
            
    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = (lon_deg + 180.0) / 360.0 * n
        ytile = (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n
        return xtile, ytile

    def num2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        return math.degrees(lat_rad), lon_deg

    def download_tile(self, x, y, zoom):
        if x < 0 or y < 0 or x >= 2 ** zoom or y >= 2 ** zoom:
            return None
        tile_name = os.path.join(str(zoom), str(x), f"{y}.png")
        tile_path = utils_path_get_asset("tiles", tile_name)
        if not os.path.exists(tile_path):
            os.makedirs(os.path.dirname(tile_path), exist_ok=True)
            url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
            headers = {
                "User-Agent": "MyGTKMapViewer/1.0 (ntkhuong.coder@gmail.com)"
            }
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req) as response, open(tile_path, 'wb') as out_file:
                    out_file.write(response.read())
                LOG_DEBUG(f"Downloaded tile {tile_path}")
            except Exception as e:
                LOG_ERR(f"Download error for tile {x},{y}: {e}")
                return None
        return tile_path
    
    def set_zoom(self, new_zoom):
        new_zoom = max(1, min(new_zoom, 19))
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            self.tiles.clear()
            self.queue_draw()
            LOG_DEBUG(f"Zoom set to {self.zoom}")

    def stop(self):
        LOG_DEBUG(f"🛑 Map view stopped.")