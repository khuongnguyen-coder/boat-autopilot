"""
app.py

This module initializes the GTK application, handles user authentication,
loads resources and styles, and launches the main view if login succeeds.

Features:
    - User authentication with bcrypt password hashing
    - Resource (GResource) loading for assets
    - CSS injection for consistent UI styling
    - Login dialog flow with error handling
    - Launches MainView upon successful login

Dependencies:
    - GTK 3 (gi.repository)
    - bcrypt for password validation
    - utils.log for logging
    - utils.path for path management
    - views.main_view.MainView
    - views.login_dialog.LoginDialog

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import gi
gi.require_version("Gtk", "3.0")

import json
import bcrypt

from gi.repository import Gtk, Gdk, Gio

from views.main_view import MainView
from views.login_dialog import LoginDialog

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("main")["info"]
LOG_DEBUG = utils_log_get_logger("main")["debug"]
LOG_WARN  = utils_log_get_logger("main")["warn"]
LOG_ERR   = utils_log_get_logger("main")["err"]

from utils.path import utils_path_get_users
from config import ENABLE_FEATURE_TILE_DOWNLOAD_RUNTIME


# --------------------------------------------------------------------------------------------
def authenticate(username: str, password: str) -> bool:
    """
    Check credentials against stored bcrypt hashes in users.json.

    Args:
        username (str): Username entered by the user.
        password (str): Plain-text password entered by the user.

    Returns:
        bool: True if credentials match, False otherwise.
    """
    users_list = utils_path_get_users()
    try:
        with open(users_list, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return False

    users = data.get("users", {})
    stored_hash = users.get(username)

    if not stored_hash:
        return False  # username not found

    # bcrypt expects bytes
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
# --------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------
class VnestAutopilot(Gtk.Application):
    """
    Main GTK Application class for Vnest Autopilot.

    Handles startup (resource + CSS loading) and activation (authentication
    flow and launching the main view).
    """

    def __init__(self):
        """Initialize the application with a unique ID."""
        super().__init__(application_id="vn.vnest.autopilot")

    def do_startup(self):
        """Perform startup tasks: load resources and apply CSS styling."""
        Gtk.Application.do_startup(self)

        # Register GResource before loading any UI
        try:
            resource = Gio.Resource.load("resources.gresource")
            Gio.resources_register(resource)
        except Exception as e:
            LOG_ERR(f"Failed to load resources.gresource: {e}")

        # Load CSS from resource
        css = Gtk.CssProvider()
        css.load_from_resource("/vn/vnest/autopilot/ui/css/style.css")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def do_activate(self):
        """
        Activate the application:
        - Show login dialog and authenticate user
        - If valid, launch MainView
        - If canceled, exit gracefully
        """
        authenticated = False

        while not authenticated:
            login = LoginDialog()
            response = login.run()

            if response == Gtk.ResponseType.OK:
                username, password = login.get_credentials()
                if authenticate(username, password):
                    LOG_INFO("Login success !!!")
                    authenticated = True
                    login.destroy()
                    main_view = MainView(self)
                    main_view.window.present()
                else:
                    # Invalid login → show error dialog
                    md = Gtk.MessageDialog(
                        transient_for=login,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text="Invalid username or password!",
                    )
                    md.run()
                    md.destroy()
                    login.destroy()
            else:
                LOG_INFO("Login canceled !!!")
                login.destroy()
                return  # exit the app if canceled
# --------------------------------------------------------------------------------------------
