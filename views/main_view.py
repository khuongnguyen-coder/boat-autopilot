import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from views.map_view import MapView
from views.camera_view import CameraView

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("main_view")["info"]
LOG_DEBUG = utils_log_get_logger("main_view")["debug"]
LOG_WARN  = utils_log_get_logger("main_view")["warn"]
LOG_ERR   = utils_log_get_logger("main_view")["err"]

class MainView:
    def __init__(self, app):
        builder = Gtk.Builder()
        builder.add_from_resource("/vn/vnest/autopilot/ui/main.glade")

        self.window = builder.get_object("main_window")
        self.window.set_title("Vnest Autopilot")
        self.window.set_application(app)

        # ✅ Connect destroy before showing window
        self.window.connect("destroy", self.on_destroy)

        # === Notebook & Boxes ===
        self.notebook = builder.get_object("main_notebook")
        self.box_camera = builder.get_object("window_box_camera")
        self.box_map = builder.get_object("window_box_map")

        # === Map View Setup ===
        self.box_map = builder.get_object("window_box_map")
        if self.box_map:
            self.box_map.set_hexpand(True)
            self.box_map.set_vexpand(True)

            LOG_DEBUG("Initializing MapView...")
            self.map_view = MapView()
            self.map_view.set_hexpand(True)
            self.map_view.set_vexpand(True)

            self.box_map.pack_start(self.map_view, expand=True, fill=True, padding=0)
            self.box_map.show_all()
            LOG_DEBUG("MapView initialized successfully")
        else:
            LOG_ERR("❌ Could not find 'window_box_map' in UI.")

        # === Camera View Setup ===
        self.box_camera = builder.get_object("window_box_camera")
        if self.box_camera:
            self.box_camera.set_hexpand(True)
            self.box_camera.set_vexpand(True)
            self.box_camera.set_halign(Gtk.Align.FILL)
            self.box_camera.set_valign(Gtk.Align.FILL)

            LOG_DEBUG("Initializing CameraView...")
            self.camera_view = CameraView()
            self.camera_view.set_hexpand(True)
            self.camera_view.set_vexpand(True)
            self.camera_view.set_halign(Gtk.Align.FILL)
            self.camera_view.set_valign(Gtk.Align.FILL)

            self.box_camera.pack_start(self.camera_view, expand=True, fill=True, padding=0)
            self.box_camera.show_all()
            LOG_DEBUG("CameraView initialized successfully")
            LOG_DEBUG("Camera is paused by default case first tab is not belong to camera")
            self.camera_view.pause()
        else:
            LOG_ERR("❌ Could not find 'window_box_camera' in UI.")

        # === Connect notebook tab change ===
        self.notebook.connect("switch-page", self.on_switch_page)

        # === Show main window ===
        self.window.show_all()
        self.window.maximize()

    def on_switch_page(self, notebook, page, page_num):
        page_widget = notebook.get_nth_page(page_num)
        if page_widget == self.box_camera:
            LOG_DEBUG("Camera tab active → Starting stream")
            self.camera_view.resume()
        else:
            LOG_DEBUG("Camera tab not active → Pausing stream")
            self.camera_view.pause()

    def on_destroy(self, *args):
        LOG_DEBUG("Shutting down MainView...")
        if hasattr(self, "camera_view"):
            LOG_DEBUG("Stopping CameraView...")
            self.camera_view.stop()
        if hasattr(self, "map_view"):
            LOG_DEBUG("Stopping MapView...")
            self.map_view.stop()

        app = self.window.get_application()
        if app:
            app.quit()
        else:
            Gtk.main_quit()
