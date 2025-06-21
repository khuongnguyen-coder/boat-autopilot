import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, Gio

from views.main_view import MainView

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("main")["info"]
LOG_DEBUG = utils_log_get_logger("main")["debug"]
LOG_WARN  = utils_log_get_logger("main")["warn"]
LOG_ERR   = utils_log_get_logger("main")["err"]

class VnestAutopilot(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="vn.vnest.autopilot")

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # ✅ Register the GResource before loading any UI
        try:
            resource = Gio.Resource.load("resources.gresource")
            Gio.resources_register(resource)
        except Exception as e:
            LOG_ERR(f"Failed to load resources.gresource: {e}")

        # ✅ Load CSS from resource
        css = Gtk.CssProvider()
        css.load_from_resource("/vn/vnest/autopilot/ui/css/style.css")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def do_activate(self):
        main_view = MainView(self)         # Instantiate the MainView
        main_view.window.present()