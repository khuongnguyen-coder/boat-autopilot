"""
main_view.py

Main GTK window and controller for the VNest Autopilot application.

Responsibilities:
    - Initialize Map, Camera, and Settings views
    - Manage notebook tabs (locking, unlocking, preventing unwanted switches)
    - Handle global lifecycle (startup, shutdown, resource cleanup)

Author: Khuong Nguyen <ntkhuong.coder@gmail.com>
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GLib

# === Project Imports ===
from views.map_view import MapView
from views.camera_view import CameraView
from views.setting_view import SettingView
from views.map.map_visualize import MapVisualize

from utils.dialogs import utils_dialog_info_dialog
from utils.log import utils_log_get_logger

# === Logger Setup ===
LOG_INFO  = utils_log_get_logger("main_view")["info"]
LOG_DEBUG = utils_log_get_logger("main_view")["debug"]
LOG_WARN  = utils_log_get_logger("main_view")["warn"]
LOG_ERR   = utils_log_get_logger("main_view")["err"]


# ==============================================================================
# Main Application View
# ==============================================================================
class MainView:
    """
    Main GTK window for VNEST Autopilot.
    Handles initialization of notebook tabs, views, and global state.
    """

    def __init__(self, app):
        # ----------------------------------------------------------------------
        # Load UI from Glade
        # ----------------------------------------------------------------------
        builder = Gtk.Builder()
        builder.add_from_resource("/vn/vnest/autopilot/ui/main.glade")

        self.map_visualize = MapVisualize()

        self.window = builder.get_object("main_window")
        self.window.set_title("Vnest Autopilot")
        self.window.set_application(app)

        # Connect destroy before showing window
        self.window.connect("destroy", self.on_destroy)

        # ----------------------------------------------------------------------
        # Notebook Setup
        # ----------------------------------------------------------------------
        self.notebook = builder.get_object("main_notebook")

        # ----------------------------------------------------------------------
        # Map View
        # ----------------------------------------------------------------------
        self.box_map = builder.get_object("window_box_map")
        if self.box_map:
            self._init_map_view()
        else:
            LOG_ERR("[ERR] Could not find 'window_box_map' in UI.")

        # ----------------------------------------------------------------------
        # Camera View
        # ----------------------------------------------------------------------
        self.box_camera = builder.get_object("window_box_camera")
        if self.box_camera:
            self._init_camera_view()
        else:
            LOG_ERR("[ERR] Could not find 'window_box_camera' in UI.")

        # ----------------------------------------------------------------------
        # Setting View
        # ----------------------------------------------------------------------
        self.box_setting = builder.get_object("window_box_setting")
        if self.box_setting:
            self._init_setting_view(builder)
        else:
            LOG_ERR("[ERR] Could not find 'window_box_setting' in UI.")

        # ----------------------------------------------------------------------
        # Notebook Tab Change Handler
        # ----------------------------------------------------------------------
        self.notebook.connect("switch-page", self.on_switch_page)

        # ----------------------------------------------------------------------
        # Show Main Window
        # ----------------------------------------------------------------------
        self.window.maximize()
        self.window.show_all()

        # Force notebook to last page + lock other tabs
        GLib.idle_add(self._init_notebook_state)

        # Show reminder dialog after window is visible
        GLib.idle_add(lambda: utils_dialog_info_dialog(
            self.window, "Please, choose extent to continue .."
        ))

    # ==========================================================================
    # Init Helper Methods
    # ==========================================================================
    def _init_map_view(self):
        LOG_DEBUG("Initializing MapView ...")
        self.box_map.set_hexpand(True)
        self.box_map.set_vexpand(True)

        self.map_view = MapView(self.map_visualize)
        self.map_view.set_hexpand(True)
        self.map_view.set_vexpand(True)

        self.box_map.pack_start(self.map_view, expand=True, fill=True, padding=0)
        self.box_map.show_all()
        LOG_DEBUG("MapView initialized successfully")

    def _init_camera_view(self):
        LOG_DEBUG("Initializing CameraView ...")
        self.box_camera.set_hexpand(True)
        self.box_camera.set_vexpand(True)
        self.box_camera.set_halign(Gtk.Align.FILL)
        self.box_camera.set_valign(Gtk.Align.FILL)

        self.camera_view = CameraView()
        self.camera_view.set_hexpand(True)
        self.camera_view.set_vexpand(True)
        self.camera_view.set_halign(Gtk.Align.FILL)
        self.camera_view.set_valign(Gtk.Align.FILL)

        self.box_camera.pack_start(self.camera_view, expand=True, fill=True, padding=0)
        self.box_camera.show_all()
        LOG_DEBUG("CameraView initialized successfully")

        # Pause camera by default unless camera tab is selected
        LOG_DEBUG("Camera is paused by default (first tab is not camera).")
        self.camera_view.pause()

    def _init_setting_view(self, builder):
        LOG_DEBUG("Initializing SettingView ...")
        self.setting_view = SettingView(builder, self)
        LOG_DEBUG("SettingView initialized successfully")

    # ==========================================================================
    # Notebook Tab State
    # ==========================================================================
    def _init_notebook_state(self):
        total_pages = self.notebook.get_n_pages()
        self._locked = True  # flag to track lock state
        self._allowed_page = total_pages - 1

        if self._allowed_page >= 0:
            # Force last page as active
            self.notebook.set_current_page(self._allowed_page)

            # Gray out other tabs
            for i in range(total_pages - 1):
                tab_label = self.notebook.get_tab_label(self.notebook.get_nth_page(i))
                if tab_label:
                    tab_label.set_sensitive(False)

    def unlock_tabs(self):
        """Re-enable all locked tabs once user has chosen extent."""
        self._locked = False
        total_pages = self.notebook.get_n_pages()
        for i in range(total_pages):
            tab_label = self.notebook.get_tab_label(self.notebook.get_nth_page(i))
            if tab_label:
                tab_label.set_sensitive(True)

        # Defer the page change so it happens after GTK processes unlock
        GLib.idle_add(lambda: self.notebook.set_current_page(total_pages - 1))

    # ==========================================================================
    # Notebook Event Handlers
    # ==========================================================================
    def on_change_page(self, notebook, scrollable, page_num):
        """Intercept page changes to enforce lock state."""
        LOG_DEBUG(f"User trying to change to {page_num}, locked={self._locked}")

        if getattr(self, "_locked", False) and page_num != self._allowed_page:
            LOG_DEBUG(f"Blocked change → staying on {self._allowed_page}")
            return True  # returning True cancels the page change

        return False  # allow change

    def on_switch_page(self, notebook, page, page_num):
        """Handle tab switch events and camera start/stop logic."""
        if getattr(self, "_locked", False) and page_num != self._allowed_page:
            LOG_DEBUG(f"Blocked tab switch → staying on {self._allowed_page}")
            notebook.emit_stop_by_name("switch-page")  # prevent tab change
            return

        # Camera start/stop logic
        page_widget = notebook.get_nth_page(page_num)
        if page_widget == self.box_camera:
            LOG_DEBUG("Camera tab active → Starting stream")
            self.camera_view.resume()
        else:
            LOG_DEBUG("Camera tab not active → Pausing stream")
            self.camera_view.pause()

    # ==========================================================================
    # Cleanup
    # ==========================================================================
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
