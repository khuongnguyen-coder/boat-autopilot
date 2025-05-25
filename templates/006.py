import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

class MaximizedDynamicWindow(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.MaximizedDynamicApp")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        # Create the application window
        window = Gtk.ApplicationWindow(application=app)
        window.set_title("GTK4 Maximized Window Example")
        window.set_resizable(True)

        # Content example
        label = Gtk.Label(label="Window starts maximized but is not fullscreen.")
        label.set_margin_top(20)
        label.set_margin_bottom(20)
        label.set_margin_start(30)
        label.set_margin_end(30)
        window.set_child(label)

        # Show the window
        window.present()

        # Maximize it (not fullscreen)
        window.maximize()

app = MaximizedDynamicWindow()
app.run()
