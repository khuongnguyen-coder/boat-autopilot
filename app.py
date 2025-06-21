import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gio

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
            print(f"Failed to load resources.gresource: {e}")

    def do_activate(self):
        # ✅ Correct GResource path (must start with /, no .glade relative path)
        builder = Gtk.Builder()
        builder.add_from_resource("/vn/vnest/autopilot/ui/main.glade")

        window = builder.get_object("main_window")
        window.set_title("Vnest Autopilot")
        window.set_application(self)
        window.show_all()      # GTK 3 requires show_all()
        window.present()
        window.maximize()
