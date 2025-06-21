import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib

import cv2
import numpy as np

class WebcamWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Webcam Viewer")
        self.set_default_size(640, 480)

        self.image = Gtk.Image()
        self.add(self.image)

        print("🔌 Opening webcam...")
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        # Optional: Set fixed resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.cap.isOpened():
            print("❌ Could not open webcam.")
            self.image.set_from_icon_name("dialog-error", Gtk.IconSize.DIALOG)
        else:
            print("✅ Webcam opened successfully.")
            GLib.timeout_add(30, self.update_frame)

        self.connect("destroy", self.on_destroy)

    def update_frame(self):
        if not self.cap.isOpened():
            print("⚠️ Camera is not opened.")
            return False

        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("⚠️ Failed to read frame.")
            return True  # Keep trying

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame_rgb.shape

            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                frame_rgb.tobytes(),
                GdkPixbuf.Colorspace.RGB,
                False, 8,
                w, h,
                w * c
            )
            self.image.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"❌ Error converting frame: {e}")

        return True  # Keep the loop running

    def on_destroy(self, *args):
        print("🧹 Releasing camera...")
        if self.cap and self.cap.isOpened():
            self.cap.release()
        Gtk.main_quit()

if __name__ == "__main__":
    win = WebcamWindow()
    win.show_all()
    Gtk.main()
