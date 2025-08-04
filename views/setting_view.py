import gi
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, Pango

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

from views.extent.extent_manager import ExtentManager
from views.map.map_visualize import MapVisualize

class SettingView():
    def __init__(self, _builder, _map_visualize):
        super().__init__()

        # Load elements from the builder using widget IDs
        self.map_extent_combobox = _builder.get_object("setting_map_extent_combobox")
        self.map_visualize = _map_visualize
        self.map_extent_manager = ExtentManager()

        location_list = self.map_extent_manager.extent_get_location_list()
        LOG_DEBUG(f"location_list: {location_list}")

        model = Gtk.ListStore(str, object)  # (display_string, EncMetadata)

        for metadata in self.map_extent_manager.metadata_list:
            names = metadata.location_name
            if isinstance(names, list) and names:
                valid_names = [name.strip() for name in names if isinstance(name, str) and name.strip()]
                if valid_names:
                    label = ", ".join(valid_names)  # or "\n".join(valid_names) for multiline
                    model.append([label, metadata])

        self.map_extent_combobox.set_model(model)
        # Clear existing renderers to avoid duplication
        self.map_extent_combobox.clear()

        # Create renderer with wrap (not ellipsize)
        renderer = Gtk.CellRendererText()
        renderer.set_property("wrap-width", 400)
        renderer.set_property("wrap-mode", Pango.WrapMode.WORD_CHAR)

        # Apply to ComboBox
        self.map_extent_combobox.pack_start(renderer, True)
        self.map_extent_combobox.add_attribute(renderer, "text", 0)  # show column 0

        # Optional: select first item
        self.map_extent_combobox.set_active(0)

        # Connect signal
        self.map_extent_combobox.connect("changed", self.on_language_changed)
    
    def on_language_changed(self, combo):
        model = combo.get_model()
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = self.map_extent_combobox.get_model()
            selected_metadata = model[tree_iter][1]  # column 1 is EncMetadata object
            LOG_DEBUG(f"Selected ENC metadata: {selected_metadata.enc_name} : {selected_metadata.s57_path}")

            # def update_extent(self, *, tile_base_path=None, center_lat=None, center_lon=None, zoom=None):
            self.map_visualize.update_extent(selected_metadata.tile_dir,
                                            selected_metadata.center.lat,
                                            selected_metadata.center.lon,
                                            selected_metadata.zoom_range.min)
