"""
setting_view.py - Settings panel for VNEST Autopilot application.

This module defines the `SettingView` class, responsible for handling
user interactions with:
    - Map extent selection (via a ComboBox populated from ENC metadata).
    - Map layer visibility (via dynamically generated checkboxes).

It connects UI elements (from a Gtk.Builder Glade file) with the
backend map visualization logic (`MapVisualize`) and updates the map
view when the user selects a new extent or modifies layer visibility.

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import os
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, Pango

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

from config import VNEST_AUTOPILOT_DATABASE_PATH

from views.extent.extent_manager import ExtentManager
from views.map.map_visualize import MapVisualize
from views.map.map_layer_visibility import MapLayerCheckboxTable


class SettingView:
    """
    Settings panel view that manages map extent selection and layer visibility.

    Args:
        _builder (Gtk.Builder): Builder object loaded from Glade UI file.
        _mainview (MainView): Reference to the main application view.

    Behavior:
        - Populates extent ComboBox from ENC metadata.
        - Updates map visualization when extent changes.
        - Displays layer visibility checkboxes tied to `MapVisualize`.
    """

    def __init__(self, _builder, _mainview):
        super().__init__()

        # === Extent ComboBox setup ===
        self.map_extent_combobox = _builder.get_object("setting_map_extent_combobox")
        self.main_view = _mainview
        self.map_visualize = _mainview.map_visualize
        self.map_extent_manager = ExtentManager()

        # Retrieve available extents from ExtentManager
        location_list = self.map_extent_manager.extent_get_location_list()
        LOG_DEBUG(f"location_list: {location_list}")

        # Create model: (display_string, EncMetadata object)
        model = Gtk.ListStore(str, object)

        # Populate ComboBox with valid extent names
        for metadata in self.map_extent_manager.metadata_list:
            names = metadata.location_name
            if isinstance(names, list) and names:
                valid_names = [name.strip() for name in names if isinstance(name, str) and name.strip()]
                if valid_names:
                    label = ", ".join(valid_names)  # Use comma-separated string
                    model.append([label, metadata])

        # Assign model to ComboBox
        self.map_extent_combobox.set_model(model)
        self.map_extent_combobox.clear()

        # Configure text renderer with word wrapping
        renderer = Gtk.CellRendererText()
        renderer.set_property("wrap-width", 400)
        renderer.set_property("wrap-mode", Pango.WrapMode.WORD_CHAR)

        # Apply renderer to show the display string (column 0)
        self.map_extent_combobox.pack_start(renderer, True)
        self.map_extent_combobox.add_attribute(renderer, "text", 0)

        # Start with no default selection
        self.map_extent_combobox.set_active(-1)

        # Connect change handler
        self.map_extent_combobox.connect("changed", self.on_extent_changed)

        # === Layer visibility checkbox table ===
        map_layer_visibility = _builder.get_object("map_layer_visibility_vewport")
        self.map_layer_visibility_table = MapLayerCheckboxTable()
        self.map_layer_visibility_table.map_visualize_ref = self.map_visualize
        map_layer_visibility.add(self.map_layer_visibility_table)

    # ----------------------------------------------------------------------

    def on_extent_changed(self, combo):
        """
        Handle ComboBox selection change.

        - Updates map extent in `MapVisualize`.
        - Updates layer visibility checkboxes.
        - Loads GeoJSON overlays for the new extent.
        - Unlocks main notebook tabs (so user can switch views).
        """
        model = combo.get_model()
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = self.map_extent_combobox.get_model()
            selected_metadata = model[tree_iter][1]  # column 1 = EncMetadata

            LOG_DEBUG(f"Selected ENC metadata: {selected_metadata.enc_name} : {selected_metadata.s57_path}")

            # Update new extent data in MapVisualize
            self.map_visualize.update_extent(
                selected_metadata.tile_dir,
                selected_metadata.center.lat,
                selected_metadata.center.lon,
                selected_metadata.zoom_range
            )

            # Refresh layer visibility table with new extent's layers
            layers_data = selected_metadata.layers
            self.map_layer_visibility_table.update_layers_config(layers_data)

            # Load corresponding GeoJSON directory
            geojson_dir = os.path.join(
                VNEST_AUTOPILOT_DATABASE_PATH,
                selected_metadata.geojson_dir
            )
            LOG_DEBUG(f"Selected GEOJSON dir: {geojson_dir}")
            self.map_visualize.layers_update(geojson_dir, self.map_layer_visibility_table)

            # Unlock main notebook tabs (user can now navigate away)
            self.main_view.unlock_tabs()
