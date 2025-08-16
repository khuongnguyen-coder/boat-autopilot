import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_visualize")["info"]
LOG_DEBUG = utils_log_get_logger("map_visualize")["debug"]
LOG_WARN  = utils_log_get_logger("map_visualize")["warn"]
LOG_ERR   = utils_log_get_logger("map_visualize")["err"]

class LoginDialog(Gtk.Dialog):
    def __init__(self, parent=None):
        # Create a dialog window with a title and optional parent
        super().__init__(title="VNEST Autopilot Login", transient_for=parent, flags=0)

        # Add Cancel and OK buttons at the bottom of the dialog
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        # Set the default size of the dialog
        self.set_default_size(350, 150)

        # Create a grid layout for aligning labels and input fields
        box = self.get_content_area()
        grid = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)
        box.add(grid)

        # --- Username field ---
        self.username_entry = Gtk.Entry()
        self.username_entry.set_text("admin")  # Default username
        grid.attach(Gtk.Label(label="Username:"), 0, 0, 1, 1)  # Label at row 0, column 0
        grid.attach(self.username_entry, 1, 0, 1, 1)            # Entry at row 0, column 1

        # --- Password field ---
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)  # Hide password characters (●●●)
        self.password_entry.set_text("123")        # Default password
        grid.attach(Gtk.Label(label="Password:"), 0, 1, 1, 1)  # Label at row 1, column 0
        grid.attach(self.password_entry, 1, 1, 1, 1)           # Entry at row 1, column 1

        # Show all widgets in the dialog
        self.show_all()

    def get_credentials(self):
        """Return (username, password) entered in the dialog"""
        return self.username_entry.get_text(), self.password_entry.get_text()
