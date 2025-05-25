import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from utils.path import utils_path_get_asset
from utils.path import utils_path_get_ui_xml

# Define constants
BOX_WIDTH = 600  # Width of the info box in pixels

class InfoView(Gtk.Box):
    def __init__(self):
        super().__init__()

        # Load builder and UI
        ui_path = utils_path_get_ui_xml("info_view.ui")
        builder = Gtk.Builder.new_from_file(ui_path)
        main_box = builder.get_object("main_box")

        if main_box is None:
            raise RuntimeError("Failed to load main_box from UI file")

        print("main_box:", main_box)
        print("Type:", type(main_box))

        child = main_box.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            main_box.remove(child)
            self.append(child)
            child = next_child

        # Keep references to widgets for later updates
        self.speed_label = builder.get_object("speed_label")
        self.boat_image = builder.get_object("boat_image")
        self.lat_label = builder.get_object("lat_label")
        self.lon_label = builder.get_object("lon_label")

    def set_boat_image(self, filepath):
        self.boat_image.set_from_file(filepath)

    def update_info(self, speed=None, lat=None, lon=None):
        if speed is not None:
            self.speed_label.set_text(f"Speed: {speed:.1f} knots")
        if lat is not None:
            self.lat_label.set_text(f"Lat: {lat:.6f}")
        if lon is not None:
            self.lon_label.set_text(f"Lon: {lon:.6f}")
