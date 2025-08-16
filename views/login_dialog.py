"""
login_dialog.py - GTK Login Dialog for VNEST Autopilot

This module defines a reusable `LoginDialog` class that prompts the user 
for a username and password before accessing the main application. It uses 
Gtk.Dialog with a grid layout for clean alignment of input fields.

Usage:
    from views.login_dialog import LoginDialog

    login = LoginDialog(parent=main_window)
    response = login.run()
    if response == Gtk.ResponseType.OK:
        username, password = login.get_credentials()
        # Perform authentication...
    login.destroy()

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from utils.log import utils_log_get_logger

# Initialize logger for this module
LOG_INFO  = utils_log_get_logger("login_dialog")["info"]
LOG_DEBUG = utils_log_get_logger("login_dialog")["debug"]
LOG_WARN  = utils_log_get_logger("login_dialog")["warn"]
LOG_ERR   = utils_log_get_logger("login_dialog")["err"]


class LoginDialog(Gtk.Dialog):
    """
    A modal login dialog that prompts for username and password.

    Args:
        parent (Gtk.Window, optional): Parent window to attach dialog to.

    Behavior:
        - Provides username and password entry fields.
        - Includes Cancel and OK buttons.
        - Masks password input with ●●●.
        - Returns credentials via `get_credentials()`.
    """

    def __init__(self, parent=None):
        # Initialize the dialog window with title and optional parent
        super().__init__(title="VNEST Autopilot Login", transient_for=parent, flags=0)

        # Add Cancel and OK buttons at the bottom of the dialog
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        # Set default size (width=350px, height=150px)
        self.set_default_size(350, 150)

        # --- Content area setup ---
        box = self.get_content_area()

        # Use a Gtk.Grid for clean layout of labels and input fields
        grid = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)
        box.add(grid)

        # --- Username field ---
        self.username_entry = Gtk.Entry()
        self.username_entry.set_text("admin")  # Default value for testing/demo
        grid.attach(Gtk.Label(label="Username:"), 0, 0, 1, 1)   # Column 0, Row 0
        grid.attach(self.username_entry, 1, 0, 1, 1)            # Column 1, Row 0

        # --- Password field ---
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)  # Hide characters (●●●)
        self.password_entry.set_text("123")        # Default value for testing/demo
        grid.attach(Gtk.Label(label="Password:"), 0, 1, 1, 1)   # Column 0, Row 1
        grid.attach(self.password_entry, 1, 1, 1, 1)            # Column 1, Row 1

        # Ensure all widgets are visible
        self.show_all()

    def get_credentials(self):
        """
        Return the username and password entered by the user.

        Returns:
            tuple: (username, password) as strings.
        """
        return self.username_entry.get_text(), self.password_entry.get_text()
