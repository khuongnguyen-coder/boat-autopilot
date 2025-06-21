import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from views.map.map_visualize import MapVisualize

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

class MapView(Gtk.Overlay):
    def __init__(self):
        super().__init__()
        # 📍 Add the map view first
        self.map_visualize = MapVisualize()
        self.add(self.map_visualize)

        # ➕ Zoom In button
        self.btn_zoom_in = Gtk.Button(label="+")
        self.btn_zoom_in.set_size_request(32, 32)
        self.btn_zoom_in.set_margin_top(10)
        self.btn_zoom_in.set_margin_end(10)
        self.btn_zoom_in.set_halign(Gtk.Align.END)
        self.btn_zoom_in.set_valign(Gtk.Align.START)
        self.btn_zoom_in.connect("clicked", self.on_zoom_in)
        self.add_overlay(self.btn_zoom_in)

        # ➖ Zoom Out button
        self.btn_zoom_out = Gtk.Button(label="-")
        self.btn_zoom_out.set_size_request(32, 32)
        self.btn_zoom_out.set_margin_top(52)
        self.btn_zoom_out.set_margin_end(10)
        self.btn_zoom_out.set_halign(Gtk.Align.END)
        self.btn_zoom_out.set_valign(Gtk.Align.START)
        self.btn_zoom_out.connect("clicked", self.on_zoom_out)
        self.add_overlay(self.btn_zoom_out)

    def on_zoom_in(self, button):
        self.map_visualize.set_zoom(self.map_visualize.zoom + 1)

    def on_zoom_out(self, button):
        self.map_visualize.set_zoom(self.map_visualize.zoom - 1)
