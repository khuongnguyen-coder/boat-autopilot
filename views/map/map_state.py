"""
map_state.py - Map state container for VNEST Autopilot.

This module defines the `MapState` class, which encapsulates the current state of the
map rendering system. It tracks the following:

    - Map center (lat/lon) and GPS location.
    - Ship marker (custom drawable object).
    - Zoom range and current zoom level.
    - Panning offsets and drag state.
    - Tile rendering (cached Cairo surfaces).
    - User interaction states (mouse clicks, dragging).
    - Debug mode toggle for diagnostics.

Usage:
    from views.map.map_state import MapState

    state = MapState(center_lat, center_lon, (min_zoom, max_zoom))
    state.my_ship_marker.set_location(lat, lon)
    state.curr_zoom = 10

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

from utils.path import utils_path_get_asset
from views.map.map_marker.marker_ship import MapMarkerShip


class MapState:
    """
    Holds the current state of the map (center, zoom, tiles, interaction, ship marker).

    Attributes:
        center_loc_lat (float): Current map center latitude.
        center_loc_lon (float): Current map center longitude.
        gps_loc_lat (float): GPS latitude of the ship.
        gps_loc_lon (float): GPS longitude of the ship.
        my_ship_marker (MapMarkerShip): Custom ship marker object with heading and label.
        zoom_range (tuple): (min_zoom, max_zoom) available levels.
        curr_zoom (int): Current zoom level.
        offset_x (int): Horizontal pan offset in pixels.
        offset_y (int): Vertical pan offset in pixels.
        tiles_dir_path (str|None): Path to tile storage directory.
        tiles (dict): Map of {(x, y): Cairo surface} tile cache.
        last_clicked_pos (tuple): Last mouse click position (x, y).
        dragging (bool): True if drag operation is active.
        drag_start_x (int): X coordinate where drag began.
        drag_start_y (int): Y coordinate where drag began.
        debug_mode (bool): Toggle for diagnostic overlays.
    """

    def __init__(self, _center_lat: float, _center_lon: float, _zoom_range: tuple):
        """
        Initialize a MapState instance.

        Args:
            _center_lat (float): Initial map center latitude.
            _center_lon (float): Initial map center longitude.
            _zoom_range (tuple): (min_zoom, max_zoom) zoom levels.
        """
        # Current location (map center in lat/lon)
        self.center_loc_lat = _center_lat
        self.center_loc_lon = _center_lon

        # GPS location (start same as center)
        self.gps_loc_lat = _center_lat
        self.gps_loc_lon = _center_lon

        # Ship marker setup
        self.my_ship_marker = MapMarkerShip(
            image_path=utils_path_get_asset("map", "ship.png"),
            size=24
        )
        self.my_ship_marker.set_location(self.gps_loc_lat, self.gps_loc_lon)
        self.my_ship_marker.set_heading(0)  # Default north

        # Zooming
        self.zoom_range = _zoom_range
        self.curr_zoom = self.zoom_range[0]  # Start with minimum zoom

        # Panning offsets
        self.offset_x = 0
        self.offset_y = 0

        # Tile rendering cache
        self.tiles_dir_path = None
        self.tiles = {}

        # Interaction state
        self.last_clicked_pos = (0, 0)
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Debugging option
        self.debug_mode = False
