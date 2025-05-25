import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio
from views.main_view import MainView

class VnestAutopilot(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.vnest.autopilot",)
    
    def do_activate(self):
        window = MainView(self)
        # Show the window
        window.present()
        # Maximize it (not fullscreen)
        window.maximize()

    def do_startup(self):
        Gtk.Application.do_startup(self)