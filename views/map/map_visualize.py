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
from views.map.map_state import MapState

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

        self.map_state = MapState(MY_LOCATION_LON, MY_LOCATION_LAT, (6, 19))
        
        LOG_DEBUG("MapVisualize init done")

    def on_button_press(self, widget, event):
        LOG_DEBUG(f"on_button_press: {event.x}, {event.y}, button={event.button}")
        
        # Only respond to left mouse button (button 1)
        if event.button != 1:
            return False  # Ignore other buttons

        # Handle left-click: begin drag and register as click
        self.map_state.dragging = True
        self.map_state.drag_start_x = event.x
        self.map_state.drag_start_y = event.y
        self.start_offset_x = self.map_state.offset_x
        self.start_offset_y = self.map_state.offset_y

        # Also treat this as a click for coordinate detection
        self.on_map_clicked(event.x, event.y)

        return True

    def on_scroll(self, widget, event):
        old_zoom = self.map_state.curr_zoom

        if event.direction == Gdk.ScrollDirection.UP:
            self.map_state.curr_zoom = min(self.map_state.curr_zoom + 1, self.map_state.zoom_range[1])  # limit zoom max
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.map_state.curr_zoom = max(self.map_state.curr_zoom - 1, self.map_state.zoom_range[0])   # limit zoom min
        else:
            return False

        LOG_DEBUG(f"Zoom changed: {old_zoom} → {self.map_state.curr_zoom}")

        self.map_state.tiles.clear()  # clear cached tiles to reload
        self.queue_draw()
        return True

    def on_motion_notify(self, widget, event):
        if self.map_state.dragging:
            dx = event.x - self.map_state.drag_start_x
            dy = event.y - self.map_state.drag_start_y
            self.map_state.offset_x = self.start_offset_x + dx
            self.map_state.offset_y = self.start_offset_y + dy
            self.queue_draw()
        return True

    def on_button_release(self, widget, event):
        if event.button == 1 and self.map_state.dragging:
            self.map_state.dragging = False
            dx = -self.map_state.offset_x / TILE_SIZE
            dy = -self.map_state.offset_y / TILE_SIZE
            cx, cy = self.deg2num(self.map_state.center_loc_lat, self.map_state.center_loc_lon, self.map_state.curr_zoom)
            new_cx = cx + dx
            new_cy = cy + dy
            self.map_state.center_loc_lat, self.map_state.center_loc_lon = self.num2deg(new_cx, new_cy, self.map_state.curr_zoom)
            self.map_state.offset_x = 0
            self.map_state.offset_y = 0
            self.queue_draw()
        return True

    def on_map_clicked(self, x, y):
        LOG_DEBUG(f"on_map_clicked: {x}, {y}")
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        center_xtile, center_ytile = self.deg2num(self.map_state.center_loc_lat, self.map_state.center_loc_lon, self.map_state.curr_zoom)

        tiles_x = math.ceil(width / TILE_SIZE) + 2
        tiles_y = math.ceil(height / TILE_SIZE) + 2

        start_xtile = int(center_xtile - tiles_x // 2)
        start_ytile = int(center_ytile - tiles_y // 2)

        offset_x = -((center_xtile - int(center_xtile)) * TILE_SIZE) + self.map_state.offset_x
        offset_y = -((center_ytile - int(center_ytile)) * TILE_SIZE) + self.map_state.offset_y

        clicked_xtile = (x - offset_x) / TILE_SIZE + start_xtile
        clicked_ytile = (y - offset_y) / TILE_SIZE + start_ytile

        lat, lon = self.num2deg(clicked_xtile, clicked_ytile, self.map_state.curr_zoom)
        self.map_state.last_clicked_pos = (lat, lon)
        LOG_DEBUG(f"Clicked at pixel ({x:.0f}, {y:.0f}) => Coordinates: ({lat:.6f}, {lon:.6f})")
        self.queue_draw()

    def on_draw(self, widget, ctx):
        # LOG_DEBUG("on_draw called")
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        
        lat = self.map_state.center_loc_lat
        lon = self.map_state.center_loc_lon
        zoom = self.map_state.curr_zoom

        LOG_DEBUG(f"*** on_draw -> center_lat: {lat}, center_lon: {lon}, curr_zoom: {zoom}")

        center_x, center_y = self.deg2num(lat, lon, zoom)

        tiles_x = math.ceil(width / TILE_SIZE) + 2
        tiles_y = math.ceil(height / TILE_SIZE) + 2
        start_x = int(center_x - tiles_x // 2)
        start_y = int(center_y - tiles_y // 2)

        # Force center_loc to be in center of widget
        offset_x = width / 2 - (center_x - start_x) * TILE_SIZE + self.map_state.offset_x
        offset_y = height / 2 - (center_y - start_y) * TILE_SIZE + self.map_state.offset_y

        for i in range(tiles_x):
            for j in range(tiles_y):
                x = start_x + i
                y = start_y + j
                tile_path = self.query_tile(x, y, self.map_state.curr_zoom)
                # LOG_DEBUG(f"Tile path: {tile_path}")
                if tile_path:
                    try:
                        key = f"{self.map_state.curr_zoom}/{x}/{y}"
                        if key not in self.map_state.tiles:
                            self.map_state.tiles[key] = GdkPixbuf.Pixbuf.new_from_file(tile_path)
                        pixbuf = self.map_state.tiles[key]
                        draw_x = round(i * TILE_SIZE + offset_x)
                        draw_y = round(j * TILE_SIZE + offset_y)
                        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, draw_x, draw_y)
                        ctx.paint()
                    except Exception as e:
                        LOG_ERR(f"Error drawing tile {x},{y}: {e}")

        # Draw real-time GPS location (not necessarily center of map)
        if self.map_state.gps_loc_lat is not None and self.map_state.gps_loc_lon is not None:
            gps_xtile, gps_ytile = self.deg2num(self.map_state.gps_loc_lat, self.map_state.gps_loc_lon, self.map_state.curr_zoom)
            gps_px = round((gps_xtile - start_x) * TILE_SIZE + offset_x - self.map_state.gps_loc_pixbuf.get_width() / 2)
            gps_py = round((gps_ytile - start_y) * TILE_SIZE + offset_y - self.map_state.gps_loc_pixbuf.get_height())

            if 0 <= gps_px < width and 0 <= gps_py < height:
                Gdk.cairo_set_source_pixbuf(ctx, self.map_state.gps_loc_pixbuf, gps_px, gps_py)
                ctx.paint()
                LOG_DEBUG(f"[✓] Draw GPS marker at ({gps_px}, {gps_py})")
            else:
                LOG_DEBUG(f"[ ] GPS marker out of view: ({gps_px}, {gps_py})")

    def deg2num(self, lat_deg, lon_deg, zoom):
        LOG_DEBUG(f"deg2num input -> lat: {lat_deg}, lon: {lon_deg}, zoom: {zoom}")

        # Clamp lat deg
        lat_deg = max(min(lat_deg, 85.0511), -85.0511)

        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom

        try:
            tan_val = math.tan(lat_rad)
            cos_val = math.cos(lat_rad)
            log_val = math.log(tan_val + 1 / cos_val)
        except Exception as e:
            LOG_ERR(f"deg2num math fail -> lat_rad: {lat_rad}, tan: {tan_val}, cos: {cos_val}, zoom: {zoom}")
            raise

        x_tile = (lon_deg + 180.0) / 360.0 * n
        y_tile = (1.0 - log_val / math.pi) / 2.0 * n
        return x_tile, y_tile


    def num2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        return math.degrees(lat_rad), lon_deg

    def query_tile(self, x, y, zoom):
        if x < 0 or y < 0 or x >= 2 ** zoom or y >= 2 ** zoom:
            return None

        tile_name = os.path.join(str(zoom), str(x), f"{y}.png")
        
        # LOG_DEBUG(f" * tiles_dir_path: {self.map_state.tiles_dir_path}")
        # LOG_DEBUG(f" * tile_name: {tile_name}")

        # Case 1: tiles_dir_path is set
        if self.map_state.tiles_dir_path:
            tile_path = os.path.join(self.map_state.tiles_dir_path, tile_name)
        else:
            # fallback to empty tile
            tile_path = utils_path_get_asset("tiles", G_TILE_EMPTY)
            LOG_DEBUG(f"[✗] tiles_dir_path not set, using empty tile: {tile_path}")
            return tile_path
            # return None

        # LOG_DEBUG(f"Check tile path: {tile_path}")

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
                    return utils_path_get_asset("tiles", G_TILE_EMPTY)
                    # return None
            else:
                tile_path = utils_path_get_asset("tiles", G_TILE_EMPTY)
                # tile_path = None
                # LOG_DEBUG(f"[✗] Tile not found and downloading disabled. Using empty: {tile_path}")


        # LOG_DEBUG(f"tile_path: {tile_path}")
        return tile_path

    def set_zoom(self, new_zoom):
        new_zoom = max(self.map_state.zoom_range[0], min(new_zoom, self.map_state.zoom_range[1]))
        if new_zoom != self.map_state.curr_zoom:
            self.map_state.curr_zoom = new_zoom
            self.map_state.tiles.clear()
            self.queue_draw()
            LOG_DEBUG(f"Zoom set to {self.map_state.curr_zoom}")

    def set_zoom_in(self):
        LOG_DEBUG(f"Zoom range: [{self.map_state.zoom_range[0]}, {self.map_state.zoom_range[1]}]")
        new_zoom = min(self.map_state.curr_zoom + 1, self.map_state.zoom_range[1])
        
        if new_zoom != self.map_state.curr_zoom:
            self.map_state.curr_zoom = new_zoom
            self.map_state.tiles.clear()
            self.queue_draw()
            LOG_DEBUG(f"Zoom in (set to {self.map_state.curr_zoom})")


    def set_zoom_out(self):
        LOG_DEBUG(f"Zoom range: [{self.map_state.zoom_range[0]}, {self.map_state.zoom_range[1]}]")
        
        # Giảm zoom xuống 1, nhưng không nhỏ hơn zoom tối thiểu
        new_zoom = max(self.map_state.curr_zoom - 1, self.map_state.zoom_range[0])
        
        if new_zoom != self.map_state.curr_zoom:
            self.map_state.curr_zoom = new_zoom
            self.map_state.tiles.clear()
            self.queue_draw()
            LOG_DEBUG(f"Zoom out (set to {self.map_state.curr_zoom})")


    # def go_my_location(self):
    #     self.map_state.center_loc_lat = self.map_state.gps_loc_lat
    #     self.map_state.center_loc_lon = self.map_state.gps_loc_lon
    #     self.map_state.offset_x = 0
    #     self.map_state.offset_y = 0
    #     self.map_state.curr_zoom = self.map_state.curr_zoom
    #     self.map_state.tiles.clear()
    #     self.queue_draw()
    #     LOG_DEBUG(f"Centered map at my location: ({self.map_state.center_loc_lat}, {self.map_state.center_loc_lon})")

    def go_my_location(self):
        """
        Center the map on the current GPS location.
        """
        if self.map_state.gps_loc_lat is None or self.map_state.gps_loc_lon is None:
            LOG_WARN("[✗] No GPS location set — cannot go to my location.")
            return

        self.map_state.center_loc_lat = self.map_state.gps_loc_lat
        self.map_state.center_loc_lon = self.map_state.gps_loc_lon
        self.map_state.offset_x = 0
        self.map_state.offset_y = 0

        # Clear tile cache to force re-render
        self.map_state.tiles.clear()

        self.queue_draw()
        LOG_DEBUG(f"[✓] Map centered at GPS location: ({self.map_state.center_loc_lat:.6f}, {self.map_state.center_loc_lon:.6f})")


    def get_center_location(self):
        """
        Returns the current center location of the map as a (lat, lon) tuple.
        """
        return (self.map_state.center_loc_lat, self.map_state.center_loc_lon)

    def update_gps_location(self, lat, lon):
        """
        Update the map view to center on the specified latitude and longitude.
        """
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            LOG_WARN(f"Ignored invalid center location: lat={lat}, lon={lon}")
            return

        self.map_state.gps_loc_lat = lat
        self.map_state.gps_loc_lon = lon
        self.map_state.offset_x = 0
        self.map_state.offset_y = 0
        self.queue_draw()
        LOG_DEBUG(f"Center updated to: ({lat:.6f}, {lon:.6f})")

    def start_center_location_simulator(self, interval_ms=1000):
        """
        Start a simulated center location updater (moves east slightly every second).
        """
        self._simulator_running = True
        self._simulated_lat = self.map_state.gps_loc_lat
        self._simulated_lon = self.map_state.gps_loc_lon

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

    def update_extent(self, tile_base_path=None, center_lat=None, center_lon=None, zoom_range=None):
        """
        Update the map's extent, tile source, and zoom level — only if all parameters are valid.

        Parameters:
            tile_base_path (str): Path to tile folder (must be a directory).
            center_lat (float): Latitude in range [-90, 90].
            center_lon (float): Longitude in range [-180, 180].
            zoom_range (tuple or object): Zoom range (tuple/list of 2 ints, or object with .min and .max).
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

        # --- Validate zoom_range ---
        parsed_zoom_range = None

        if zoom_range is not None:
            if isinstance(zoom_range, (tuple, list)):
                if (
                    len(zoom_range) == 2 and
                    all(isinstance(z, int) for z in zoom_range) and
                    1 <= zoom_range[0] <= zoom_range[1] <= 19
                ):
                    parsed_zoom_range = (zoom_range[0], zoom_range[1])
                    LOG_DEBUG(f"[✓] Valid zoom range (tuple/list): {parsed_zoom_range}")
                else:
                    LOG_WARN(f"[✗] Invalid zoom range (tuple/list): {zoom_range}")
                    valid = False
            elif hasattr(zoom_range, 'min') and hasattr(zoom_range, 'max'):
                if (
                    isinstance(zoom_range.min, int) and
                    isinstance(zoom_range.max, int) and
                    1 <= zoom_range.min <= zoom_range.max <= 19
                ):
                    parsed_zoom_range = (zoom_range.min, zoom_range.max)
                    LOG_DEBUG(f"[✓] Valid zoom range (ZoomRange): {parsed_zoom_range}")
                else:
                    LOG_WARN(f"[✗] Invalid zoom range (ZoomRange values): {zoom_range}")
                    valid = False
            else:
                LOG_WARN(f"[✗] Invalid zoom range (unsupported type): {zoom_range}")
                valid = False

        # --- Apply only if all valid ---
        if valid:
            if tile_base_path:
                self.map_state.tiles_dir_path = full_tile_path
            if center_lat is not None and center_lon is not None:
                self.map_state.center_loc_lat = center_lat
                self.map_state.center_loc_lon = center_lon
                self.map_state.gps_loc_lat = center_lat
                self.map_state.gps_loc_lon = center_lon
            if parsed_zoom_range:
                self.map_state.zoom_range = parsed_zoom_range
                self.map_state.curr_zoom = parsed_zoom_range[0]

            self.map_state.offset_x = 0
            self.map_state.offset_y = 0
            self.map_state.tiles.clear()
            self.queue_draw()

            LOG_DEBUG("[✓] update_extent applied")
        else:
            LOG_WARN("[✗] update_extent aborted due to invalid parameters")



    def handler_pan_up(self):
        self.map_state.offset_y += 100
        self.queue_draw()
    
    def handler_pan_down(self):
        self.map_state.offset_y -= 100
        self.queue_draw()
    
    def handler_pan_left(self):
        self.map_state.offset_x += 100
        self.queue_draw()

    def handler_pan_right(self):
        self.map_state.offset_x -= 100
        self.queue_draw()


