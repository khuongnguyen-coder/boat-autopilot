"""
utils/dialogs.py

Utility functions for showing GTK message dialogs (Error, Warning, Info).
Provides both a generic message dialog and convenient shortcut wrappers.

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

from gi.repository import Gtk

def _utils_dialog_message_dialog(parent, text: str, title: str = "Message",
                                 message_type: Gtk.MessageType = Gtk.MessageType.INFO,
                                 use_markup: bool = True):
    """
    Show a simple message dialog with optional markup and centered button.

    Args:
        parent (Gtk.Window): The parent window/dialog
        text (str): The message to display (markup allowed if use_markup=True)
        title (str): Title of the dialog
        message_type (Gtk.MessageType): INFO, WARNING, ERROR, QUESTION
        use_markup (bool): Whether to parse text as Pango markup
    """
    md = Gtk.MessageDialog(
        transient_for=parent,
        flags=0,
        message_type=message_type,
        buttons=Gtk.ButtonsType.OK,
    )
    md.set_title(title)
    md.set_default_size(350, 150)

    # Set main text with markup if enabled
    if use_markup:
        md.set_markup(f"<b>{title}</b>")
        md.format_secondary_markup(text)
    else:
        md.set_text(title)
        md.format_secondary_text(text)

    # Center the action area (buttons)
    action_area = md.get_action_area()
    action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)

    md.run()
    md.destroy()

def utils_dialog_error_dialog(parent, text: str, title: str = "Error"):
    """
    Shortcut for showing an error dialog.
    """
    _utils_dialog_message_dialog(parent, text, title, Gtk.MessageType.ERROR)


def utils_dialog_warning_dialog(parent, text: str, title: str = "Warning"):
    """
    Shortcut for showing a warning dialog.
    """
    _utils_dialog_message_dialog(parent, text, title, Gtk.MessageType.WARNING)


def utils_dialog_info_dialog(parent, text: str, title: str = "Reminder"):
    """
    Shortcut for showing an info/reminder dialog.
    """
    _utils_dialog_message_dialog(parent, text, title, Gtk.MessageType.INFO)
