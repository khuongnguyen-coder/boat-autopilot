import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib

import cv2
import threading
import time

class CameraApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Threaded Camera App")
        self.set_default_size(640, 480)

        self.image = Gtk.Image()
        self.add(self.image)

        self.frame = None
        self.running = True

        # Start OpenCV camera in background thread
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            print("[ERR] Failed to open camera.")
            self.image.set_from_icon_name("dialog-error", Gtk.IconSize.DIALOG)
            return

        # Start background thread to read frames
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()

        # Update the UI regularly (fast but non-blocking)
        GLib.timeout_add(30, self.update_image)

        self.connect("destroy", self.on_quit)

    def capture_loop(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            time.sleep(0.01)  # Slight delay to reduce CPU

    def update_image(self):
        if self.frame is not None:
            try:
                frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, c = frame_rgb.shape
                pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                    frame_rgb.tobytes(),
                    GdkPixbuf.Colorspace.RGB,
                    False, 8, w, h, w * c
                )
                self.image.set_from_pixbuf(pixbuf)
            except Exception as e:
                print(f"[ERR] Frame conversion error: {e}")
        return True  # Keep updating

    def on_quit(self, *args):
        print("🧹 Releasing camera...")
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        Gtk.main_quit()

if __name__ == "__main__":
    app = CameraApp()
    app.show_all()
    Gtk.main()
