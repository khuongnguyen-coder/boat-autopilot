import gi
import math
import urllib.request
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib


TILE_SIZE = 256  # Standard tile size
ZOOM = 16
CENTER_LAT, CENTER_LON = 10.8382543, 106.8317088

class MapArea(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.connect("resize", self.on_resize)
        self.set_draw_func(self.on_draw)
        self.tiles = {}

    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile

    def num2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    def on_resize(self, area, width, height):
        self.queue_draw()

    def download_tile(self, x, y, zoom):
        path = f"tiles/{zoom}/{x}/{y}.png"
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
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
        return path if os.path.exists(path) else None

    def on_draw(self, area, ctx, width, height):
        center_x, center_y = self.deg2num(CENTER_LAT, CENTER_LON, ZOOM)

        tiles_x = math.ceil(width / TILE_SIZE) + 2
        tiles_y = math.ceil(height / TILE_SIZE) + 2

        start_x = int(center_x - tiles_x // 2)
        start_y = int(center_y - tiles_y // 2)

        offset_x = -((center_x - int(center_x)) * TILE_SIZE)
        offset_y = -((center_y - int(center_y)) * TILE_SIZE)

        for i in range(tiles_x):
            for j in range(tiles_y):
                x = start_x + i
                y = start_y + j

                tile_path = self.download_tile(x, y, ZOOM)
                if tile_path:
                    try:
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(tile_path)
                        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, i * TILE_SIZE + offset_x, j * TILE_SIZE + offset_y)
                        ctx.paint()
                    except Exception as e:
                        print(f"Error loading tile {tile_path}: {e}")


class MapWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Multi Tile Map Viewer")
        self.set_default_size(800, 600)

        map_area = MapArea()
        self.set_child(map_area)

class MapApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.MultiTileMap")

    def do_activate(self):
        win = MapWindow(self)
        win.present()

if __name__ == "__main__":
    app = MapApplication()
    app.run()
