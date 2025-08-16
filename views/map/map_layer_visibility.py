"""
map_layer_visibility.py - Layer visibility control panel for ENC map layers.

This module defines `MapLayerCheckboxTable`, a GTK widget that displays a grid of
checkboxes for Electronic Navigational Chart (ENC) layers. It allows users to:

    - Toggle visibility of ENC layers dynamically.
    - Update checkbox states from metadata (enabled/disabled, active/inactive).
    - Track newly discovered ENC layers and persist them to `.new_layers.txt`.
    - Query currently active (visible) layers.

Usage:
    from views.map.map_layer_visibility import MapLayerCheckboxTable

    table = MapLayerCheckboxTable()
    table.map_visualize_ref = map_visualize_instance
    table.update_layers_config(layers_dict)
    active_layers = table.get_active_layers()

Dependencies:
    - GTK 3 (Gtk, Pango).
    - utils.log for logging.

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import json
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_layer_visibility")["info"]
LOG_DEBUG = utils_log_get_logger("map_layer_visibility")["debug"]
LOG_WARN  = utils_log_get_logger("map_layer_visibility")["warn"]
LOG_ERR   = utils_log_get_logger("map_layer_visibility")["err"]

# Predefined ENC layer list
ENC_LAYER_LIST = [
    "ACHARE", "ACHBRT", "AIRARE", "BCNLAT", "BCNSAW", "BCNSPP",
    "BOYCAR", "BOYISD", "BOYLAT", "BOYSAW", "BOYSPP",
    "BRIDGE", "BUAARE", "BUISGL", "C_AGGR", "CBLOHD", "COALNE",
    "CTSARE", "CTNARE", "DAYMAR", "DEPARE", "DEPCNT", "DSID",
    "FAIRWY", "FLODOC", "FSHFAC", "HRBARE", "LAKARE", "LIGHTS",
    "LNDMRK", "LNDARE", "LNDELV", "LNDRGN", "MAGVAR", "MARCUL",
    "M_COVR", "M_NSYS", "M_QUAL", "M_SREL", "NAVLNE", "OBSTRN",
    "PILBOP", "PILPNT", "PONTON", "RAILWY", "RECTRC", "RESARE",
    "RIVERS", "ROADWY", "RUNWAY", "SBDARE", "SEAARE", "SILTNK",
    "SISTAT", "SLCONS", "SLOTOP", "SOUNDG", "TOPMAR", "UNSARE",
    "UWTROC"
]

# File where unknown/new layers are logged
NEW_LAYERS_FILE = ".new_layers.txt"


class MapLayerCheckboxTable(Gtk.Box):
    """
    GTK widget displaying a table of ENC layer visibility checkboxes.

    Attributes:
        checkboxes (dict): Maps layer name → Gtk.CheckButton widget.
        handlers (dict): Maps layer name → signal handler IDs (for toggling).
        curr_layers_dict (dict): Stores current active/inactive state for layers.
        map_visualize_ref: Reference to a MapVisualize instance (for callbacks).
    """

    def __init__(self):
        """Initialize the checkbox table with predefined ENC layers."""
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.START)

        # Layout grid for checkboxes
        self.grid = Gtk.Grid(column_spacing=20, row_spacing=20)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.START)

        self.checkboxes = {}
        self.handlers = {}  # store signal handler IDs

        # Create one checkbox per layer
        for i, layer in enumerate(sorted(ENC_LAYER_LIST)):
            checkbox = Gtk.CheckButton(label=layer)
            checkbox.modify_font(Pango.FontDescription("14"))
            checkbox.set_size_request(150, -1)
            checkbox.set_sensitive(False)

            handler_id = checkbox.connect("toggled", self.on_checkbox_toggled, layer)
            self.handlers[layer] = handler_id
            self.checkboxes[layer] = checkbox

            # Arrange in a 6-column grid
            self.grid.attach(checkbox, i % 6, i // 6, 1, 1)

        self.pack_start(self.grid, False, False, 0)

    def on_checkbox_toggled(self, checkbox, layer):
        """
        Callback triggered when the user toggles a checkbox.

        Args:
            checkbox (Gtk.CheckButton): The checkbox widget.
            layer (str): ENC layer identifier.
        """
        state = checkbox.get_active()
        self.curr_layers_dict[layer] = state
        LOG_DEBUG(f"[TOGGLE] {layer} => {state}")

        # Notify the map visualization about visibility changes
        if hasattr(self, "map_visualize_ref") and self.map_visualize_ref:
            self.map_visualize_ref.layers_visibility_toggle(layer, state)    
    
    def update_layers_config(self, layers_dict):
        """
        Update the checkboxes based on provided layer configuration.

        Args:
            layers_dict (dict): Mapping of {layer_name: bool}.
        """
        self.curr_layers_dict = layers_dict

        # Detect and log new/unknown layers
        for layer in layers_dict.keys():
            if layer not in ENC_LAYER_LIST:
                with open(NEW_LAYERS_FILE, "a") as f:
                    f.write(layer + "\n")

        # Update checkbox states and sensitivity
        for layer, checkbox in self.checkboxes.items():
            handler_id = self.handlers[layer]
            checkbox.handler_block(handler_id)  # block signal to avoid recursion

            if layer in layers_dict:
                checkbox.set_sensitive(True)
                checkbox.set_active(bool(layers_dict[layer]))
            else:
                checkbox.set_active(False)
                checkbox.set_sensitive(False)

            checkbox.handler_unblock(handler_id)  # re-enable signal

    def is_layer_active(self, layer):
        """
        Check if the given layer's checkbox is active.

        Args:
            layer (str): ENC layer identifier.

        Returns:
            bool: True if active, False otherwise.
        """
        checkbox = self.checkboxes.get(layer)
        return checkbox.get_active() if checkbox else False

    def get_active_layers(self):
        """
        Get a list of all currently active layers.

        Returns:
            list[str]: Names of active ENC layers.
        """
        return [layer for layer, cb in self.checkboxes.items() if cb.get_active()]
