import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

from utils.path import utils_path_get_asset

# map_state.py
class MapState:
    def __init__(self, _center_lat, _center_lot, _zoom_range):

        # Current location (map center in lat/lon)
        self.center_loc_lat = _center_lat       # float: Current latitude (map center)
        self.center_loc_lon = _center_lot       # float: Current longitude (map center)
        # center_pixbuf_path = utils_path_get_asset("map", "marker.png")
        # self.center_loc_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(center_pixbuf_path, 24, 24)

        self.gps_loc_lat = _center_lat                 # float: GPS latitude
        self.gps_loc_lon = _center_lot                 # float: GPS longitude
        gps_pixbuf_path = utils_path_get_asset("map", "ship.png")
        self.gps_loc_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(gps_pixbuf_path, 24, 24)

        self.zoom_range = _zoom_range           # tuple: Zoom range level
        self.curr_zoom = self.zoom_range[0]     # int: Zoom level default is min level        

        # Offset for panning (in pixels)
        self.offset_x = 0               # int
        self.offset_y = 0               # int

        # Tile rendering
        self.tiles_dir_path = None      # str: Path to stored tiles
        self.tiles = {}                 # dict: {(x, y): tile_surface}

        # Interaction state
        self.last_clicked_pos = (0, 0)  # tuple: last mouse (x, y)
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Debug options
        self.debug_mode = False
