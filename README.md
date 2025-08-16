# 🛰️ VNEST Autopilot  
**MIT License © 2025 VNEST — All rights reserved**

This repository is a GTK3-based **autopilot UI system** for marine navigation,  
combining **map visualization**, **camera streaming**, and **user authentication**.

---

## 🌍 MapView — OpenStreetMap Tile Viewer

A custom GTK3 widget to render and interact with map tiles from OpenStreetMap.  
Supports smooth panning, zooming, tile caching, and ship marker rendering.

### ✨ Features
- Tile-based rendering using OpenStreetMap
- Smooth panning with mouse drag
- Zoom in/out controls with overlay buttons
- GPS & ship marker support (`MapMarkerShip`)
- Extent switching via `ExtentManager`
- Layer visibility control (`MapLayerCheckboxTable`)
- Tile caching with dynamic directory loading
- Uses `Gtk.DrawingArea` for efficient redraws

---

## 🎥 CameraView — GTK3 + OpenCV Video Streamer

A `Gtk.Box` + `Gtk.DrawingArea` widget that streams live video from a webcam using OpenCV,  
rendered with Cairo/Pixbuf and aspect-ratio scaling.

### ✨ Features
- Streams video via OpenCV (`cv2.VideoCapture`)
- Auto-refreshes via GLib timeout
- Aspect ratio preserved with resize
- Pause / resume / stop controls
- Designed for embedding into main notebook tab

---

## 🔐 Authentication & User Management
- Login dialog (`LoginDialog`) prompts for username & password
- Users stored in `authentication/users.json`
- Passwords are hashed with **bcrypt**
- Configurable path resolution via `utils.path.utils_path_get_users`

---

## ⚙️ Core Components

### 🗂️ **Extent Manager**
- Loads ENC metadata (`*_metadata.json`) from `database/`
- Provides extent selection for maps
- Updates available layers + geojson data

### 🧩 **Map Layers**
- Layer visibility toggles managed by `MapLayerCheckboxTable`
- Auto-detects new ENC layers not in known list
- Supports persistence of enabled/disabled states

### 🚢 **Ship Marker**
- `MapMarkerShip` draws a rotatable ship icon
- Displays ship name above marker
- Hit detection for click interactions

### 🧭 **Map State**
- Manages zoom, center, offsets, tiles, ship marker
- Handles dragging & interaction state
- Keeps debug and overlay info

---

## 📦 Dependencies

### System packages (Ubuntu/Debian):
```sh
sudo apt install -y \
    python3-gi \
    gir1.2-gtk-3.0 \
    gir1.2-pango-1.0 \
    libgdk-pixbuf2.0-dev \
    python3-opencv \
    python3-bcrypt

#### Python packages:
pip install numpy opencv-python

# 📜 License
MIT License
© 2025 VNEST — All rights reserved.