import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

from views.map_view import MapView

from views.info_view import BOX_WIDTH
from views.info_view import InfoView

from utils.path import utils_path_get_asset

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("main_view")["info"]
LOG_DEBUG = utils_log_get_logger("main_view")["debug"]
LOG_WARN  = utils_log_get_logger("main_view")["warn"]
LOG_ERR   = utils_log_get_logger("main_view")["err"]

class MainView(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("VNEST Autopilot")
        self.set_resizable(True)
        # Set the default size of the window
        self.set_default_size(400, 300)

        # Create horizontal box container
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.set_margin_top(5)
        main_box.set_margin_bottom(5)
        main_box.set_margin_start(5)
        main_box.set_margin_end(5)

        # Left box: Boat information
        info_box = Gtk.Box()
        info_box.set_size_request(BOX_WIDTH, -1)  # width=200, height=-1 (no fixed height)
        # info_box.set_hexpand(True)
        # info_box.set_vexpand(True)
        info_box.set_css_classes(["info-box"])

        # Right box: Map and controls
        map_box = Gtk.Box()
        map_box.set_hexpand(True)
        map_box.set_vexpand(True)
        map_box.set_css_classes(["map-box"])

        # Add left and right boxes to the horizontal container
        main_box.append(info_box)
        main_box.append(map_box)
        
        # Create a vertical box to stack map and its controls
        # main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Map Content
        map_view = MapView()
        # Let map_area expand to fill available space
        map_view.set_vexpand(True)
        map_view.set_hexpand(True)
        # Add the map view to the main box
        map_box.append(map_view)

        # Info Content
        info_view = InfoView()
        boat_img_path = utils_path_get_asset("info", "vehicle.png")
        info_view.set_boat_image(boat_img_path)
        info_view.update_info(speed=12.3, lat=37.7749, lon=-122.4194)
        info_box.append(info_view)

        # Set the main box as the child of the window
        self.set_child(main_box)
        

    def on_activate(self, app):
        # Create the application window
        window = Gtk.ApplicationWindow(application=app)
        window.set_resizable(True)

        # Content example
        label = Gtk.Label(label="Window starts maximized but is not fullscreen.")
        label.set_margin_top(20)
        label.set_margin_bottom(20)
        label.set_margin_start(30)
        label.set_margin_end(30)
        window.set_child(label)