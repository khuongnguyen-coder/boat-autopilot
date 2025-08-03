import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

from views.extent.extent_manager import ExtentManager

class SettingView():
    def __init__(self, builder):
        super().__init__()

        # Load elements from the builder using widget IDs
        self.map_extent_combobox = builder.get_object("setting_map_extent_combobox")

        self.map_extent_manager = ExtentManager()

        languages = ["English", "Tiếng Việt", "Français", "Español"]
        model = Gtk.ListStore(str)
        for lang in languages:
            model.append([lang])
        self.map_extent_combobox.set_model(model)

        # Optional: select first item
        self.map_extent_combobox.set_active(0)

        # Connect signal
        self.map_extent_combobox.connect("changed", self.on_language_changed)
    
    def on_language_changed(self, combo):
        model = combo.get_model()
        active_index = combo.get_active()
        if active_index >= 0:
            selected = model[active_index][0]
            LOG_DEBUG(f"Selected language: {selected}")