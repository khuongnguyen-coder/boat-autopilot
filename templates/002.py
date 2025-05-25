import gi
import math
import urllib.request
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, GdkPixbuf, Gdk

TILE_SIZE = 256
ZOOM = 16

class MapArea(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_draw_func(self.on_draw)

        self.center_lat = 10.8382543
        self.center_lon = 106.8317088
        self.offset_x = 0
        self.offset_y = 0
        self.tiles = {}

        # Create a drag gesture controller for the map
        self.drag = Gtk.GestureDrag.new()
        self.drag.connect("drag-begin", self.on_drag_begin)
        self.drag.connect("drag-update", self.on_drag_update)
        self.drag.connect("drag-end", self.on_drag_end)

        # Attach the drag gesture controller to the MapArea widget
        self.add_controller(self.drag)

    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = (lon_deg + 180.0) / 360.0 * n
        ytile = (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n
        return xtile, ytile

    def num2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    def download_tile(self, x, y, zoom):
        if x < 0 or y < 0 or x >= 2 ** zoom or y >= 2 ** zoom:
            return None

        path = f"tiles/{zoom}/{int(x)}/{int(y)}.png"
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            url = f"https://tile.openstreetmap.org/{zoom}/{int(x)}/{int(y)}.png"
            headers = {
                "User-Agent": "MyGTKMapViewer/1.0 (ntkhuong.coder@gmail.com)"
            }
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                    out_file.write(response.read())
            except Exception as e:
                print(f"Failed to download tile {x},{y}: {e}")
                return None
        return path

    def on_draw(self, area, ctx, width, height):
        center_x, center_y = self.deg2num(self.center_lat, self.center_lon, ZOOM)

        tiles_x = math.ceil(width / TILE_SIZE) + 2
        tiles_y = math.ceil(height / TILE_SIZE) + 2

        start_x = int(center_x - tiles_x // 2)
        start_y = int(center_y - tiles_y // 2)

        offset_x = -((center_x - int(center_x)) * TILE_SIZE) + self.offset_x
        offset_y = -((center_y - int(center_y)) * TILE_SIZE) + self.offset_y

        for i in range(tiles_x):
            for j in range(tiles_y):
                x = start_x + i
                y = start_y + j
                tile_path = self.download_tile(x, y, ZOOM)
                if tile_path:
                    try:
                        key = f"{ZOOM}/{x}/{y}"
                        if key not in self.tiles:
                            self.tiles[key] = GdkPixbuf.Pixbuf.new_from_file(tile_path)
                        pixbuf = self.tiles[key]
                        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, i * TILE_SIZE + offset_x, j * TILE_SIZE + offset_y)
                        ctx.paint()
                    except Exception as e:
                        print(f"Error loading tile {tile_path}: {e}")

    def on_drag_begin(self, gesture, start_x, start_y):
        self.drag_start_x = self.offset_x
        self.drag_start_y = self.offset_y

    def on_drag_update(self, gesture, offset_x, offset_y):
        self.offset_x = self.drag_start_x + offset_x
        self.offset_y = self.drag_start_y + offset_y
        self.queue_draw()

    def on_drag_end(self, gesture, offset_x, offset_y):
        center_x, center_y = self.deg2num(self.center_lat, self.center_lon, ZOOM)
        dx = -self.offset_x / TILE_SIZE
        dy = -self.offset_y / TILE_SIZE
        new_x = center_x + dx
        new_y = center_y + dy
        self.center_lat, self.center_lon = self.num2deg(new_x, new_y, ZOOM)

        self.offset_x = 0
        self.offset_y = 0
        self.queue_draw()


class MapWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Map Viewer with Drag")
        self.set_default_size(800, 600)

        map_area = MapArea()
        self.set_child(map_area)


class MapApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.GTKMapPan")

    def do_activate(self):
        win = MapWindow(self)
        win.present()


if __name__ == "__main__":
    app = MapApplication()
    app.run()
