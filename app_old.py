import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio
from views.main_view import MainView

# Register the compiled GResource before building UI
Gio.Resource.load("resources.gresource").register()

class VnestAutopilot(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.vnest.autopilot",)
    
    def do_activate(self):
        # window = MainView(self)
        # # Show the window
        # window.present()
        # # Maximize it (not fullscreen)
        # window.maximize()
        try:
            resource = Gio.Resource.load("resources.gresource")
            resource.register()
        except Exception as e:
            print(f"Failed to load resources.gresource: {e}")

    def do_startup(self):
        Gtk.Application.do_startup(self)


import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio
from views.main_view import MainView

class VnestAutopilot(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.vnest.autopilot")

    def do_startup(self):
        # Register the compiled GResource before any UI loads
        Gtk.Application.do_startup(self)

        try:
            resource = Gio.Resource.load("resources.gresource")
            resource.register()
        except Exception as e:
            print(f"Failed to load resources.gresource: {e}")

    def do_activate(self):
        window = MainView(self)
        window.present()
        window.maximize()
