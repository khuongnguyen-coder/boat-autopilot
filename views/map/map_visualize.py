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

MY_LOCATION_LAT = 10.8382543
MY_LOCATION_LON = 106.8317088

from config import ENABLE_FEATURE_TILE_DOWNLOAD_RUNTIME
from config import VNEST_AUTOPILOT_DATABASE_PATH

G_TILE_EMPTY = "empty.png"

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

        self.center_lat = MY_LOCATION_LAT
        self.center_lon = MY_LOCATION_LON
        self.zoom = ZOOM
        self.offset_x = 0
        self.offset_y = 0
        self.tiles_dir_path = None
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
                tile_path = self.query_tile(x, y, self.zoom)
                # LOG_DEBUG(f"Tile path: {tile_path}")
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

    def query_tile(self, x, y, zoom):
        if x < 0 or y < 0 or x >= 2 ** zoom or y >= 2 ** zoom:
            return None

        tile_name = os.path.join(str(zoom), str(x), f"{y}.png")
        
        # LOG_DEBUG(f" * tiles_dir_path: {self.tiles_dir_path}")
        # LOG_DEBUG(f" * tile_name: {tile_name}")

        # Case 1: tiles_dir_path is set
        if self.tiles_dir_path:
            tile_path = os.path.join(self.tiles_dir_path, tile_name)
        else:
            # fallback to empty tile
            tile_path = utils_path_get_asset("tiles", G_TILE_EMPTY)
            LOG_DEBUG(f"[✗] tiles_dir_path not set, using empty tile: {tile_path}")
            # return tile_path
            return None

        LOG_DEBUG(f"Check tile path: {tile_path}")

        # Check if tile exists
        if not os.path.exists(tile_path):
            if ENABLE_FEATURE_TILE_DOWNLOAD_RUNTIME:
                os.makedirs(os.path.dirname(tile_path), exist_ok=True)
                url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
                headers = {
                    "User-Agent": "MyGTKMapViewer/1.0 (ntkhuong.coder@gmail.com)"
                }
                req = urllib.request.Request(url, headers=headers)
                try:
                    with urllib.request.urlopen(req) as response, open(tile_path, 'wb') as out_file:
                        out_file.write(response.read())
                    LOG_DEBUG(f"[✓] Downloaded tile: {tile_path}")
                except Exception as e:
                    LOG_ERR(f"[✗] Download error for tile {x},{y}: {e}")
                    # return utils_path_get_asset("tiles", G_TILE_EMPTY)
                    return None
            else:
                # tile_path = utils_path_get_asset("tiles", G_TILE_EMPTY)
                tile_path = None
                # LOG_DEBUG(f"[✗] Tile not found and downloading disabled. Using empty: {tile_path}")


        # LOG_DEBUG(f"tile_path: {tile_path}")
        return tile_path

    def set_zoom(self, new_zoom):
        new_zoom = max(1, min(new_zoom, 19))
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            self.tiles.clear()
            self.queue_draw()
            LOG_DEBUG(f"Zoom set to {self.zoom}")

    def go_my_location(self):
        # Set to a default location (e.g., Ho Chi Minh City)
        self.center_lat = MY_LOCATION_LAT
        self.center_lon = MY_LOCATION_LON
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = ZOOM
        self.tiles.clear()
        self.queue_draw()
        LOG_DEBUG(f"Centered map at my location: ({self.center_lat}, {self.center_lon})")

    def get_center_location(self):
        """
        Returns the current center location of the map as a (lat, lon) tuple.
        """
        return (self.center_lat, self.center_lon)

    def update_center_location(self, lat, lon):
        """
        Update the map view to center on the specified latitude and longitude.
        """
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            LOG_WARN(f"Ignored invalid center location: lat={lat}, lon={lon}")
            return

        self.center_lat = lat
        self.center_lon = lon
        self.offset_x = 0
        self.offset_y = 0
        self.queue_draw()
        LOG_DEBUG(f"Center updated to: ({lat:.6f}, {lon:.6f})")

    def start_center_location_simulator(self, interval_ms=1000):
        """
        Start a simulated center location updater (moves east slightly every second).
        """
        self._simulator_running = True
        self._simulated_lat = self.center_lat
        self._simulated_lon = self.center_lon

        def simulate_tick():
            if not self._simulator_running:
                return False  # stop timer

            # Simulate eastward movement
            self._simulated_lon += 0.0001
            self.update_center_location(self._simulated_lat, self._simulated_lon)

            return True  # continue timer

        GLib.timeout_add(interval_ms, simulate_tick)

    def stop_center_location_simulator(self):
        """
        Stop the simulated center location updates.
        """
        self._simulator_running = False

    def update_extent(self, tile_base_path=None, center_lat=None, center_lon=None, zoom=None):
        """
        Update the map's extent, tile source, and zoom level — only if all parameters are valid.

        Parameters:
            tile_base_path (str): Path to tile folder (must be a directory).
            center_lat (float): Latitude in range [-90, 90].
            center_lon (float): Longitude in range [-180, 180].
            zoom (int): Zoom level in range [1, 19].
        """

        valid = True

        # --- Validate tile path ---
        if tile_base_path:
            full_tile_path = os.path.join(VNEST_AUTOPILOT_DATABASE_PATH, tile_base_path)

            if os.path.isdir(full_tile_path):
                LOG_DEBUG(f"[✓] Valid tile path: {full_tile_path}")
            else:
                LOG_WARN(f"[✗] Invalid tile path (not a directory): {full_tile_path}")
                valid = False

        # --- Validate center coordinates ---
        if center_lat is not None and center_lon is not None:
            if (
                isinstance(center_lat, (int, float)) and -90 <= center_lat <= 90 and
                isinstance(center_lon, (int, float)) and -180 <= center_lon <= 180
            ):
                LOG_DEBUG(f"[✓] Valid center: ({center_lat:.6f}, {center_lon:.6f})")
            else:
                LOG_WARN(f"[✗] Invalid center coordinates: lat={center_lat}, lon={center_lon}")
                valid = False
        elif center_lat is not None or center_lon is not None:
            LOG_WARN(f"[✗] Missing one of lat/lon for center: lat={center_lat}, lon={center_lon}")
            valid = False


        # --- Validate zoom ---
        if zoom is not None:
            if isinstance(zoom, int) and 1 <= zoom <= 19:
                LOG_DEBUG(f"[✓] Valid zoom: {zoom}")
            else:
                LOG_WARN(f"[✗] Invalid zoom level: {zoom}")
                valid = False

        # --- Apply only if all valid ---
        if valid:
            if tile_base_path:
                self.tiles_dir_path = full_tile_path
            if center_lat is not None and center_lon is not None:
                self.center_lat = center_lat
                self.center_lon = center_lon
            if zoom is not None:
                self.zoom = zoom

            self.offset_x = 0
            self.offset_y = 0
            self.tiles.clear()
            self.queue_draw()

            LOG_DEBUG("[✓] update_extent applied")
        else:
            LOG_WARN("[✗] update_extent aborted due to invalid parameters")


    def handler_pan_up(self):
        self.offset_y += 100
        self.queue_draw()
    
    def handler_pan_down(self):
        self.offset_y -= 100
        self.queue_draw()
    
    def handler_pan_left(self):
        self.offset_x += 100
        self.queue_draw()

    def handler_pan_right(self):
        self.offset_x -= 100
        self.queue_draw()


