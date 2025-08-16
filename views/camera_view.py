"""
camera_view.py - GTK widget for live camera preview using OpenCV.

This module provides the `CameraView` class, a GTK Box widget that embeds
a live camera feed into the VNEST Autopilot UI. It uses OpenCV for capture
and GStreamer/V4L2 backend for efficiency. Frames are drawn on a GTK
DrawingArea at ~30 FPS using Cairo + GdkPixbuf.

Features:
    - Start, stop, pause, and resume camera capture.
    - Runs capture in a background thread to avoid blocking UI.
    - Resizes and aspect-ratio preserves frames to fit available widget size.
    - Supports embedding into GTK layouts as a reusable widget.

Usage:
    camera_view = CameraView(cam_index=0)
    some_container.add(camera_view)

Dependencies:
    - GTK 3
    - OpenCV (cv2)
    - numpy

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

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
    """
    GTK Box widget for displaying a live camera stream.

    Attributes:
        cam_index (int): Camera index for OpenCV VideoCapture (default=0).
        frame (np.ndarray|None): Last captured frame in BGR format.
        running (bool): Whether the capture thread is active.
        capture_thread (threading.Thread|None): Background frame capture thread.
        cap (cv2.VideoCapture|None): OpenCV camera capture object.
        drawing_area (Gtk.DrawingArea): GTK area where frames are rendered.
    """

    def __init__(self, cam_index: int = 0):
        """
        Initialize the CameraView.

        Args:
            cam_index (int): Camera index (default 0 for /dev/video0).
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Drawing area for camera output
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.drawing_area.set_halign(Gtk.Align.FILL)
        self.drawing_area.set_valign(Gtk.Align.FILL)
        self.drawing_area.connect("draw", self.on_draw)
        self.pack_start(self.drawing_area, True, True, 0)

        # Camera state
        self.cam_index = cam_index
        self.frame = None
        self.running = False
        self.capture_thread = None
        self.cap = None

        # Start camera immediately
        self.start_camera()

        # Timer: trigger redraw ~30 fps
        GLib.timeout_add(30, self.update_image)

    # ----------------------------------------------------------------------------------------
    # Camera control
    # ----------------------------------------------------------------------------------------
    def start_camera(self):
        """Start camera capture in a background thread."""
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
        """Stop the camera and background thread safely."""
        if self.running:
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
        """Pause camera capture (stop thread but keep widget alive)."""
        if self.running:
            LOG_INFO("[PAUSE] Pausing camera capture...")
            self.stop_camera()
        else:
            LOG_INFO("[PAUSE] Camera was stopped already.")

    def resume(self):
        """Resume camera capture if it was paused."""
        if self.running:
            return  # Already running
        LOG_INFO("[RESUME] Resuming camera capture...")
        self.start_camera()

    def stop(self):
        """Completely stop CameraView (called during shutdown)."""
        LOG_DEBUG("[STOP] Stopping CameraView...")
        self.stop_camera()
        LOG_INFO("[OK] CameraView stopped.")

    # ----------------------------------------------------------------------------------------
    # Capture & rendering
    # ----------------------------------------------------------------------------------------
    def capture_loop(self):
        """Background loop that continuously grabs frames from camera."""
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame.copy()
            time.sleep(1.0 / 30)

    def update_image(self):
        """GTK timer callback to refresh DrawingArea if new frame exists."""
        if self.frame is not None and self.running:
            self.drawing_area.queue_draw()
        return True  # keep timer alive

    def on_draw(self, widget, cr):
        """
        GTK draw callback: render the latest frame.

        Args:
            widget (Gtk.Widget): DrawingArea.
            cr (cairo.Context): Cairo drawing context.

        Returns:
            bool: False to propagate further GTK draw events.
        """
        if self.frame is None:
            return False

        # Widget size
        alloc = widget.get_allocation()
        area_w, area_h = alloc.width, alloc.height

        # Convert frame BGR → RGB
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        frame_h, frame_w = frame_rgb.shape[:2]

        # Aspect ratio fit
        aspect_frame = frame_w / frame_h
        aspect_area = area_w / area_h

        if aspect_area > aspect_frame:
            new_h = area_h
            new_w = int(new_h * aspect_frame)
        else:
            new_w = area_w
            new_h = int(new_w / aspect_frame)

        resized = cv2.resize(frame_rgb, (new_w, new_h))

        # Wrap as GdkPixbuf
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(
            resized.tobytes(),
            GdkPixbuf.Colorspace.RGB,
            False, 8,
            new_w, new_h,
            new_w * 3
        )

        # Center in widget
        Gdk.cairo_set_source_pixbuf(cr, pixbuf, (area_w - new_w) / 2, (area_h - new_h) / 2)
        cr.paint()
        return False
