import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk

import cv2
import threading
import time
import numpy as np

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("camera_view")["info"]
LOG_DEBUG = utils_log_get_logger("camera_view")["debug"]
LOG_WARN  = utils_log_get_logger("camera_view")["warn"]
LOG_ERR   = utils_log_get_logger("camera_view")["err"]

class CameraView(Gtk.Box):
    def __init__(self, cam_index=0):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.drawing_area.set_halign(Gtk.Align.FILL)
        self.drawing_area.set_valign(Gtk.Align.FILL)
        self.drawing_area.connect("draw", self.on_draw)
        self.pack_start(self.drawing_area, True, True, 0)

        self.cam_index = cam_index
        self.frame = None
        self.running = False
        self.capture_thread = None
        self.cap = None

        self.start_camera()

        # Timer for triggering draw every ~30 ms
        GLib.timeout_add(30, self.update_image)

    def start_camera(self):
        self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            LOG_ERR("[ERR] Could not open camera.")
            return

        self.running = True
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        LOG_INFO("Camera started.")

    def stop_camera(self):
        if(self.running):
            self.running = False
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=1.0)
            if self.cap and self.cap.isOpened():
                self.cap.release()
                self.cap = None
            LOG_INFO("[STOP] Camera thread stopped.")
        else:
            LOG_INFO("[STOP] Camera was stopped already.")

    def pause(self):
        if(self.running):
            LOG_INFO("[PAUSE] Pausing camera capture...")
            self.stop_camera()
        else:
            LOG_INFO("[PAUSE] Camera was stopped already.")

    def resume(self):
        if self.running:
            return  # Already running
        LOG_INFO("[RESUME] Resuming camera capture...")
        self.start_camera()

    def capture_loop(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame.copy()
            time.sleep(1.0 / 30)

    def update_image(self):
        if self.frame is not None and self.running:
            self.drawing_area.queue_draw()
        return True  # Keep timeout running

    def on_draw(self, widget, cr):
        if self.frame is None:
            return False

        alloc = widget.get_allocation()
        area_w, area_h = alloc.width, alloc.height

        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        frame_h, frame_w = frame_rgb.shape[:2]

        aspect_frame = frame_w / frame_h
        aspect_area = area_w / area_h

        if aspect_area > aspect_frame:
            new_h = area_h
            new_w = int(new_h * aspect_frame)
        else:
            new_w = area_w
            new_h = int(new_w / aspect_frame)

        resized = cv2.resize(frame_rgb, (new_w, new_h))

        pixbuf = GdkPixbuf.Pixbuf.new_from_data(
            resized.tobytes(),
            GdkPixbuf.Colorspace.RGB,
            False, 8,
            new_w, new_h,
            new_w * 3
        )

        Gdk.cairo_set_source_pixbuf(cr, pixbuf, (area_w - new_w) / 2, (area_h - new_h) / 2)
        cr.paint()
        return False

    def stop(self):
        LOG_DEBUG("[STOP] Stopping CameraView...")
        self.stop_camera()
        LOG_INFO("[OK] CameraView stopped.")

