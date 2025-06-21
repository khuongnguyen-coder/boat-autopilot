# 🛰️ VNEST Autopilot  
**MIT License © 2025 VNEST — All rights reserved**

This repository includes two core GTK3-based UI components for a boat autopilot system:

- **🗺️ MapView** — a `Gtk.DrawingArea` widget for OpenStreetMap tile rendering  
- **🎥 CameraView** — a `Gtk.DrawingArea` widget for live video streaming via OpenCV  

Both are designed to be embedded into GTK3 applications and work together in a cohesive interface.

---

## MapView — OpenStreetMap Tile Viewer

A custom GTK3 widget to render and interact with map tiles from OpenStreetMap.  
Supports smooth panning, automatic tile caching, and marker placement.

### ✨ Features

- Tile-based map rendering using OpenStreetMap
- Mouse drag to pan
- Click to drop a marker and log coordinates
- Auto-downloads missing tiles to a local directory
- Supports center marker and click marker
- Uses `Gtk.DrawingArea` for high-performance redraw

### 📦 Dependencies

#### System packages (Ubuntu/Debian):
sudo apt install python3-gi gir1.2-gtk-3.0 libgdk-pixbuf2.0-dev

#### Python packages:
pip install numpy

## CameraView — GTK3 + OpenCV Video Streamer

A Gtk.DrawingArea widget that streams live video from the webcam using OpenCV,
rendered with Cairo and Pixbuf with aspect-ratio scaling.

### ✨ Features
- Streams video using OpenCV
- GTK3 layout using Gtk.Box and Gtk.DrawingArea
- Resizes video with maintained aspect ratio
- Supports pause/resume functionality
- Designed for embedded integration in GTK apps

### 📦 Dependencies

#### System packages (Ubuntu/Debian):
sudo apt install -y python3-gi gir1.2-gtk-3.0 libgdk-pixbuf2.0-dev python3-opencv

#### Python packages:
pip install opencv-python

# 📜 License
MIT License
© 2025 VNEST — All rights reserved.

# 📁 Directory Layout

<project_root>
    ├── app.py
    ├── autorun.sh
    ├── main.py
    ├── README.md
    ├── resources.gresource
    ├── resources.xml
    ├── scripts
    │   ├── clear_pycache.sh
    │   ├── normalize_paths.sh
    │   └── update_resources.sh
    ├── ui
    │   ├── assets
    │   │   ├── icons
    │   │   ├── info
    │   │   ├── map
    │   │   └── tiles
    │   ├── css
    │   │   └── style.css
    │   ├── main.glade
    ├── utils
    │   ├── log.py
    │   └── path.py
    └── views
        ├── camera_view.py
        ├── main_view.py
        └── map_view.py
