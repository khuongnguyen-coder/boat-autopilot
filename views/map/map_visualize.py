import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject

import threading
from gi.repository import GLib

import math
import os
import urllib.request

from utils.path import utils_path_get_asset

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_visualize")["info"]
LOG_DEBUG = utils_log_get_logger("map_visualize")["debug"]
LOG_WARN  = utils_log_get_logger("map_visualize")["warn"]
LOG_ERR   = utils_log_get_logger("map_visualize")["err"]

TILE_SIZE = 256
ZOOM = 16

MY_LOCATION_LAT = 10.8382543
MY_LOCATION_LON = 106.8317088

from config import ENABLE_FEATURE_TILE_DOWNLOAD_RUNTIME
from config import VNEST_AUTOPILOT_DATABASE_PATH
from views.map.map_state import MapState
from views.map.map_layer.layer_factory import LAYER_CLASS_MAP

G_TILE_EMPTY = "empty.png"

class MapVisualize(Gtk.DrawingArea):

    # ****************************************************************************************
    # [Custom signal]
    # Define a GObject signal to notify whenever the map view changes
    __gsignals__ = {
        # No arguments, just notifies that the view (center/zoom) changed
        "view-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    # ****************************************************************************************

    # ****************************************************************************************
    # [INIT]
    def __init__(self):
        super().__init__()
        LOG_DEBUG("MapVisualize init started")

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_can_focus(True)
        self.set_focus_on_click(True)
        self.set_app_paintable(True)

        # store added layer objects
        self.layers = []

        # Enable event masks
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.STRUCTURE_MASK |
            Gdk.EventMask.SCROLL_MASK |
            Gdk.EventMask.EXPOSURE_MASK
        )

        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_button_press)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("button-release-event", self.on_button_release)
        self.connect("scroll-event", self.on_scroll)

        # self.set_size_request(800, 600)

        self.map_state = MapState(MY_LOCATION_LON, MY_LOCATION_LAT, (6, 19))

         # async tile loading state
        self.tiles_lock = threading.Lock()         # protects access to self.map_state.tiles
        self.loading_keys = set()                  # keys currently being loaded (avoid duplicate workers)
        self.empty_pixbuf = GdkPixbuf.Pixbuf.new_from_file(
            utils_path_get_asset("map", G_TILE_EMPTY)
        )
        
        LOG_DEBUG("MapVisualize init done")
    # ****************************************************************************************

    # ****************************************************************************************
    # Override for queue_draw to add emit custom signal.
    def queue_draw(self, *args, **kwargs):
        """Queue a redraw and emit view-changed."""
        super().queue_draw(*args, **kwargs)
        self.emit("view-changed")
    # ****************************************************************************************

    # ****************************************************************************************
    # [LAYER HANDLER]
    def add_layer(self, layer):
        """Add a new map layer and redraw."""
        self.layers.append(layer)
        self.queue_draw()

    def remove_layer(self, layer):
        """Remove a map layer and redraw."""
        if layer in self.layers:
            self.layers.remove(layer)
            self.queue_draw()

    def clear_layers(self):
        """Remove all layers."""
        self.layers.clear()
        self.queue_draw()
    # ****************************************************************************************

    # ****************************************************************************************
    # [EVENT HANDLER]
    def on_button_press(self, widget, event):
        LOG_DEBUG(f"on_button_press: {event.x}, {event.y}, button={event.button}")
        
        # Only respond to left mouse button (button 1)
        if event.button != 1:
            return False  # Ignore other buttons

        # Exec hit test for all layer 
        for layer in self.layers:
            if hasattr(layer, "hit_test"):
                feature = layer.hit_test(event.x, event.y, self)
                if feature:
                    info_text = layer.properties_str(layer.get_properties(feature))
                    self.show_ship_info_popup(info_text)
                    return
        
        # Exec hit test for marker
        if self.map_state.my_ship_marker.hit_test(event.x, event.y):
            self.show_ship_info_popup(self.map_state.my_ship_marker.get_info_str())
        else:
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
        if event.direction == Gdk.ScrollDirection.SMOOTH:
            if event.delta_y < 0:
                self.zoom_level_increase()
            elif event.delta_y > 0:
                self.zoom_level_decrease()
        elif event.direction == Gdk.ScrollDirection.UP:
            self.zoom_level_increase()
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.zoom_level_decrease()
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
    # ****************************************************************************************

    # ****************************************************************************************
    # [DRAW METHOD]
    def on_draw(self, widget, ctx):
        # LOG_DEBUG("on_draw called")
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        
        lat = self.map_state.center_loc_lat
        lon = self.map_state.center_loc_lon
        zoom = self.map_state.curr_zoom

        # LOG_DEBUG(f"*** on_draw -> center_lat: {lat}, center_lon: {lon}, curr_zoom: {zoom}")

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

                        # Try to get from memory cache
                        pixbuf = self._get_cached_tile(key)

                        if pixbuf is None:
                            # Not cached yet → show placeholder and load in background
                            pixbuf = self.empty_pixbuf
                            self.queue_tile_load(key, tile_path)

                        draw_x = round(i * TILE_SIZE + offset_x)
                        draw_y = round(j * TILE_SIZE + offset_y)
                        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, draw_x, draw_y)
                        ctx.paint()
                    except Exception as e:
                        LOG_ERR(f"Error drawing tile {x},{y}: {e}")

        # Draw real-time ship marker (instead of GPS pixbuf)
        if self.map_state.gps_loc_lat is not None and self.map_state.gps_loc_lon is not None:
            gps_xtile, gps_ytile = self.deg2num(
                self.map_state.gps_loc_lat,
                self.map_state.gps_loc_lon,
                self.map_state.curr_zoom
            )

            gps_px = round((gps_xtile - start_x) * TILE_SIZE + offset_x)
            gps_py = round((gps_ytile - start_y) * TILE_SIZE + offset_y)

            if 0 <= gps_px < width and 0 <= gps_py < height:
                # Update marker position
                self.map_state.my_ship_marker.set_location(self.map_state.gps_loc_lat, self.map_state.gps_loc_lon)
                # Draw marker at map coordinates
                self.map_state.my_ship_marker.draw(ctx, gps_px, gps_py, center=True)

                # LOG_DEBUG(f"[✓] Draw ship marker '{self.map_state.my_ship_marker.name}' "
                #         f"at ({gps_px}, {gps_py}) heading={self.map_state.my_ship_marker.heading}")
            else:
                LOG_DEBUG(f"[ ] Ship marker out of view: ({gps_px}, {gps_py})")
        
        # Draw all added layers
        for layer in self.layers:
            if hasattr(layer, "draw"):
                layer.draw(ctx, self)
            elif hasattr(layer, "render"):
                layer.render(ctx, self)

    def deg2num(self, lat_deg, lon_deg, zoom):
        # LOG_DEBUG(f"deg2num input -> lat: {lat_deg}, lon: {lon_deg}, zoom: {zoom}")

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

    def lonlat_to_pixels(self, lon, lat):
        """Convert lon/lat to pixel coordinates relative to the widget."""
        width = self.get_allocated_width()
        height = self.get_allocated_height()

        # Map center in tile coordinates
        center_x, center_y = self.deg2num(
            self.map_state.center_loc_lat,
            self.map_state.center_loc_lon,
            self.map_state.curr_zoom
        )

        # Target point in tile coordinates
        tile_x, tile_y = self.deg2num(lat, lon, self.map_state.curr_zoom)

        # Convert to pixel offset from center
        dx_tiles = tile_x - center_x
        dy_tiles = tile_y - center_y

        px = width / 2 + dx_tiles * 256 + self.map_state.offset_x
        py = height / 2 + dy_tiles * 256 + self.map_state.offset_y

        return px, py

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
    # ****************************************************************************************

    # ****************************************************************************************
    # [ASYN LOADING]
    def _is_tile_cached(self, key):
        with self.tiles_lock:
            return key in self.map_state.tiles

    def _get_cached_tile(self, key):
        with self.tiles_lock:
            return self.map_state.tiles.get(key)

    def _set_cached_tile(self, key, pixbuf):
        with self.tiles_lock:
            self.map_state.tiles[key] = pixbuf

    def queue_tile_load(self, key, tile_path):
        """
        Schedule a background load for a tile if it's not cached and not already loading.
        """
        if self._is_tile_cached(key):
            return
        with self.tiles_lock:
            if key in self.loading_keys:
                return
            self.loading_keys.add(key)

        # Start background worker
        t = threading.Thread(target=self._tile_loader_thread, args=(key, tile_path), daemon=True)
        t.start()

    def _tile_loader_thread(self, key, tile_path):
        """
        Worker thread: load tile from disk, then hand-off to GTK main loop.
        """
        try:
            # Loading GdkPixbuf in a thread is generally fine if we only touch GTK in the main thread.
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(tile_path) if os.path.exists(tile_path) else self.empty_pixbuf
        except Exception as e:
            LOG_ERR(f"[tile_loader] Failed to load {tile_path}: {e}")
            pixbuf = self.empty_pixbuf

        # Install into cache and trigger redraw on GTK main thread
        GLib.idle_add(self._store_loaded_tile, key, pixbuf)

    def _store_loaded_tile(self, key, pixbuf):
        """
        Runs on GTK main thread. Commit loaded pixbuf, clear 'loading' flag, and redraw.
        """
        self._set_cached_tile(key, pixbuf)
        with self.tiles_lock:
            self.loading_keys.discard(key)
        self.queue_draw()
        return False  # remove this idle handler
    # ****************************************************************************************

    # ****************************************************************************************
    # [My Ship Info Popup]
    def show_ship_info_popup(self, info_str):
        """
        Show an information popup on the map.
        info_str: string with the information to display.
        """
        # If MapVisualize is added into multiple nested containers before it reaches MapView,
        # get_parent() will only return the immediate parent, not the MapView overlay itself.

        LOG_DEBUG(f"info_str: {info_str}")
        map_view = self.get_parent()

        # Create popup content
        popup_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        popup_content.set_margin_top(10)
        popup_content.set_margin_bottom(10)
        popup_content.set_margin_start(10)
        popup_content.set_margin_end(10)
        popup_content.set_name("popup-info-box")

        label = Gtk.Label(label=info_str)
        label.set_justify(Gtk.Justification.LEFT)
        label.get_style_context().add_class("popup-info-label")

        close_btn = Gtk.Button(label="Close")
        close_btn.connect("clicked", lambda btn: map_view.hide_common_popup())

        popup_content.pack_start(label, False, False, 0)
        popup_content.pack_start(close_btn, False, False, 0)

        # Use MapView's common popup system
        if map_view:
            map_view.show_common_popup(popup_content)


    # ****************************************************************************************

    # ****************************************************************************************
    # [API]
    # ----------------------------------------------------------------------------------------
    # [API: GPS location]
    def curr_gps_location_force(self):
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

    def curr_gps_location_update(self, lat, lon, heading_deg):
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
        self.map_state.my_ship_marker.set_location(self.map_state.gps_loc_lat, self.map_state.gps_loc_lon)
        self.map_state.my_ship_marker.set_heading(heading_deg)  # or 0 if no heading
        self.queue_draw()
        LOG_DEBUG(f"GPS location updated to: ({lat:.6f}, {lon:.6f})")
    # ----------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------
    # [API: Center location]
    def curr_center_location_get(self):
        """
        Return current zoom level.
        """
        return self.map_state.center_loc_lat, self.map_state.center_loc_lon
    # ----------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------
    # [API: Simulator]
    def curr_gps_location_sim_start(self, interval_ms=1000):
        """
        Start a simulated GPS updater that moves within map bounds and changes heading.
        """
        self._simulator_running = True
        self._simulated_lat = self.map_state.gps_loc_lat
        self._simulated_lon = self.map_state.gps_loc_lon
        self._simulated_heading = 0  # degrees, 0° = north

        # Define bounding box (min/max lat/lon) around initial point
        self._sim_bounds = {
            "lat_min": self._simulated_lat - 0.01,
            "lat_max": self._simulated_lat + 0.01,
            "lon_min": self._simulated_lon - 0.01,
            "lon_max": self._simulated_lon + 0.01,
        }

        def simulate_tick():
            if not self._simulator_running:
                return False

            distance_deg = 0.0001  # step size
            rad = math.radians(self._simulated_heading)
            new_lat = self._simulated_lat + distance_deg * math.cos(rad)
            new_lon = self._simulated_lon + distance_deg * math.sin(rad)

            # Bounce logic
            if not (self._sim_bounds["lat_min"] <= new_lat <= self._sim_bounds["lat_max"]):
                self._simulated_heading = (180 - self._simulated_heading) % 360
                return True  # skip this tick, change direction

            if not (self._sim_bounds["lon_min"] <= new_lon <= self._sim_bounds["lon_max"]):
                self._simulated_heading = (-self._simulated_heading) % 360
                return True  # skip this tick, change direction

            # Apply new position
            self._simulated_lat = new_lat
            self._simulated_lon = new_lon

            # Change heading slightly each tick
            self._simulated_heading = (self._simulated_heading + 5) % 360

            self.curr_gps_location_update(
                self._simulated_lat,
                self._simulated_lon,
                self._simulated_heading
            )

            return True

        GLib.timeout_add(interval_ms, simulate_tick)


    def curr_gps_location_sim_stop(self):
        """
        Stop the simulated center location updates.
        """
        self._simulator_running = False
    # ----------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------
    # [API: Entent]
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

        # Force to stop simulation for gps update with heading change also.
        self.curr_gps_location_sim_stop()

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

            # Start simulation for gps update with heading change also.
            self.curr_gps_location_sim_start()
        else:
            LOG_WARN("[✗] update_extent aborted due to invalid parameters")
    # ----------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------
    # [API: ZOOM HANDLER]
    def zoom_level_increase(self):
        LOG_DEBUG(f"Zoom range: [{self.map_state.zoom_range[0]}, {self.map_state.zoom_range[1]}]")
        new_zoom = min(self.map_state.curr_zoom + 1, self.map_state.zoom_range[1])
        
        if new_zoom != self.map_state.curr_zoom:
            self.map_state.curr_zoom = new_zoom
            self.map_state.tiles.clear()
            self.queue_draw()
            LOG_DEBUG(f"Zoom in (set to {self.map_state.curr_zoom})")


    def zoom_level_decrease(self):
        LOG_DEBUG(f"Zoom range: [{self.map_state.zoom_range[0]}, {self.map_state.zoom_range[1]}]")
        new_zoom = max(self.map_state.curr_zoom - 1, self.map_state.zoom_range[0])
        
        if new_zoom != self.map_state.curr_zoom:
            self.map_state.curr_zoom = new_zoom
            self.map_state.tiles.clear()
            self.queue_draw()
            LOG_DEBUG(f"Zoom out (set to {self.map_state.curr_zoom})")

    def zoom_level_get_curr_value(self):
        """
        Return current zoom level.
        """
        return self.map_state.curr_zoom
    # ----------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------
        
    # ----------------------------------------------------------------------------------------
    # [API: PAN BUTTON HANDLER]
    def pan_handler_up(self):
        self.map_state.offset_y += 100
        self.queue_draw()
    
    def pan_handler_down(self):
        self.map_state.offset_y -= 100
        self.queue_draw()
    
    def pan_handler_left(self):
        self.map_state.offset_x += 100
        self.queue_draw()

    def pan_handler_right(self):
        self.map_state.offset_x -= 100
        self.queue_draw()
    # ----------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------
    # [API: UPDATE LAYER]
    def update_layers(self, geojson_path, comboxbox_table):
        active_layers = comboxbox_table.get_active_layers()
        LOG_DEBUG(f"Currently active layers: {active_layers}")

        for layer_name in active_layers:
            if layer_name in LAYER_CLASS_MAP:
                layer_info = LAYER_CLASS_MAP[layer_name]
                layer_class = layer_info["class"]

                geojson_file = os.path.join(geojson_path, f"{layer_name}.geojson")

                if os.path.exists(geojson_file):
                    layer_instance = layer_class(
                        filepath=geojson_file,
                        line_color=layer_info.get("line_color", (0, 0, 0)),
                        line_width=layer_info.get("width", 2),
                        fill_color=layer_info.get("fill_color"),
                        fill_opacity=layer_info.get("fill_opacity", 0.3)
                    )
                    self.add_layer(layer_instance)
                    LOG_DEBUG(f"Added layer: {layer_name} with style {layer_info}")
                else:
                    LOG_WARN(f"GeoJSON file not found for {layer_name}: {geojson_file}")


    # ----------------------------------------------------------------------------------------

    # ****************************************************************************************

