import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

from views.map_view import MapView

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

        # Create a vertical box to stack map and its controls
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Map Content
        map_view = MapView()
        # Let map_area expand to fill available space
        map_view.set_vexpand(True)
        map_view.set_hexpand(True)
        # Add the map view to the main box
        main_box.append(map_view)
        
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