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

NEW_LAYERS_FILE = ".new_layers.txt"

class MapLayerCheckboxTable(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.START)

        self.grid = Gtk.Grid(column_spacing=20, row_spacing=20)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.START)

        self.checkboxes = {}
        self.handlers = {}  # store signal handler IDs

        for i, layer in enumerate(sorted(ENC_LAYER_LIST)):
            checkbox = Gtk.CheckButton(label=layer)
            checkbox.modify_font(Pango.FontDescription("14"))
            checkbox.set_size_request(150, -1)
            checkbox.set_sensitive(False)

            handler_id = checkbox.connect("toggled", self.on_checkbox_toggled, layer)
            self.handlers[layer] = handler_id
            self.checkboxes[layer] = checkbox

            # 6 columns
            self.grid.attach(checkbox, i % 6, i // 6, 1, 1)


        self.pack_start(self.grid, False, False, 0)

    def on_checkbox_toggled(self, checkbox, layer):
        """Called when the user toggles a checkbox."""
        state = checkbox.get_active()
        self.curr_layers_dict[layer] = state
        print(f"[TOGGLE] {layer} => {state}")
    
    def update_layers_config(self, layers_dict):
        self.curr_layers_dict = layers_dict

        # Detect and log new layers
        for layer in layers_dict.keys():
            if layer not in ENC_LAYER_LIST:
                with open(NEW_LAYERS_FILE, "a") as f:
                    f.write(layer + "\n")

        # Update existing checkboxes
        for layer, checkbox in self.checkboxes.items():
            handler_id = self.handlers[layer]  # get handler ID
            checkbox.handler_block(handler_id)  # block signal

            if layer in layers_dict:
                checkbox.set_sensitive(True)
                checkbox.set_active(bool(layers_dict[layer]))
            else:
                checkbox.set_active(False)
                checkbox.set_sensitive(False)

            checkbox.handler_unblock(handler_id)  # unblock signal

    def is_layer_active(self, layer):
        """Return True if the given layer's checkbox is active."""
        checkbox = self.checkboxes.get(layer)
        return checkbox.get_active() if checkbox else False

    def get_active_layers(self):
        """Return a list of layers where the checkbox is active."""
        return [layer for layer, cb in self.checkboxes.items() if cb.get_active()]
