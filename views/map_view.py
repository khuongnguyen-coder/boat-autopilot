import gi
import math
import urllib.request
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, GdkPixbuf, Gdk

from utils.path import utils_path_get_asset

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

TILE_SIZE = 256
ZOOM = 16

class MapView(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_draw_func(self.on_draw)
        
        self.center_lat = 10.8382543
        self.center_lon = 106.8317088
        self.offset_x = 0
        self.offset_y = 0
        self.tiles = {}
        self.zoom = ZOOM  # Initial zoom level
        
        marker_path = utils_path_get_asset("map", "marker.png")
        self.marker_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(marker_path, 24, 24)

        # For storing clicked point
        self.clicked_latlon = None

        # Click gesture to detect map click
        self.click = Gtk.GestureClick.new()
        self.click.connect("pressed", self.on_map_clicked)
        self.add_controller(self.click)

        
        # Create a drag gesture controller for the map
        self.drag = Gtk.GestureDrag.new()
        self.drag.connect("drag-begin", self.on_drag_begin)
        self.drag.connect("drag-update", self.on_drag_update)
        self.drag.connect("drag-end", self.on_drag_end)
        
        # Attach the drag gesture controller to the MapView widget
        self.add_controller(self.drag)
    
    def on_map_clicked(self, gesture, n_press, x, y):
        width = self.get_allocated_width()
        height = self.get_allocated_height()

        center_xtile, center_ytile = self.deg2num(self.center_lat, self.center_lon, self.zoom)

        tiles_x = math.ceil(width / TILE_SIZE) + 2
        tiles_y = math.ceil(height / TILE_SIZE) + 2

        start_xtile = int(center_xtile - tiles_x // 2)
        start_ytile = int(center_ytile - tiles_y // 2)

        offset_x = -((center_xtile - int(center_xtile)) * TILE_SIZE) + self.offset_x
        offset_y = -((center_ytile - int(center_ytile)) * TILE_SIZE) + self.offset_y

        # Convert clicked pixel to tile offset
        clicked_xtile = (x - offset_x) / TILE_SIZE + start_xtile
        clicked_ytile = (y - offset_y) / TILE_SIZE + start_ytile

        lat, lon = self.num2deg(clicked_xtile, clicked_ytile, self.zoom)
        self.clicked_latlon = (lat, lon)

        LOG_DEBUG(f"Clicked at pixel ({x}, {y}) => Coordinates: ({lat:.6f}, {lon:.6f})")
        self.queue_draw()

    # Add a setter for zoom level
    def set_zoom(self, zoom):
        self.zoom = zoom
        self.queue_draw()  # Redraw the map when zoom changes
        LOG_DEBUG(f"Zoom level updated to: {self.zoom}")

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
        LOG_DEBUG(f"Downloading tile at {x}, {y} for zoom {zoom}")

        tile_name = os.path.join(str(zoom), str(int(x)), f"{int(y)}.png")
        tile_path = utils_path_get_asset("tiles", tile_name)
        if not os.path.exists(tile_path):
            os.makedirs(os.path.dirname(tile_path), exist_ok=True)
            url = f"https://tile.openstreetmap.org/{zoom}/{int(x)}/{int(y)}.png"
            headers = {
                "User-Agent": "MyGTKMapViewer/1.0 (ntkhuong.coder@gmail.com)"
            }
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req) as response, open(tile_path, 'wb') as out_file:
                    out_file.write(response.read())
                LOG_DEBUG(f"Tile downloaded: {tile_path}")
            except Exception as e:
                LOG_ERR(f"Failed to download tile {x},{y}: {e}")
                return None
        else:
            LOG_DEBUG(f"Tile found in cache: {tile_path}")
        return tile_path

    def on_draw(self, area, ctx, width, height):
        LOG_DEBUG(f"Drawing area size: {width}x{height}")

        center_x, center_y = self.deg2num(self.center_lat, self.center_lon, ZOOM)

        tiles_x = math.ceil(width / TILE_SIZE) + 2
        tiles_y = math.ceil(height / TILE_SIZE) + 2

        start_x = int(center_x - tiles_x // 2)
        start_y = int(center_y - tiles_y // 2)

        offset_x = -((center_x - int(center_x)) * TILE_SIZE) + self.offset_x
        offset_y = -((center_y - int(center_y)) * TILE_SIZE) + self.offset_y

        LOG_DEBUG(f"Offset X: {offset_x}, Offset Y: {offset_y}")
        LOG_DEBUG(f"Drawing tiles from {start_x}, {start_y} with size {tiles_x}x{tiles_y}")

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
                            LOG_DEBUG(f"Tile loaded: {tile_path}")
                        pixbuf = self.tiles[key]

                        # Round the drawing positions to integers
                        draw_x = round(i * TILE_SIZE + offset_x)
                        draw_y = round(j * TILE_SIZE + offset_y)

                        # Debugging: Check the tile positions
                        LOG_DEBUG(f"Drawing tile at {draw_x}, {draw_y} for {x},{y} at zoom {ZOOM}")

                        # Drawing the tile
                        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, draw_x, draw_y)
                        ctx.paint()  # Ensure it paints the pixbuf
                    except Exception as e:
                        LOG_ERR(f"Error loading tile {tile_path}: {e}")
                else:
                    LOG_DEBUG(f"Tile not found for {x},{y} at zoom {ZOOM}")

        # Calculate pixel position of center marker
        center_xtile, center_ytile = self.deg2num(self.center_lat, self.center_lon, self.zoom)
        start_xtile = int(center_xtile - tiles_x // 2)
        start_ytile = int(center_ytile - tiles_y // 2)

        pixel_x = round((center_xtile - start_xtile) * TILE_SIZE + offset_x - self.marker_pixbuf.get_width() / 2)
        pixel_y = round((center_ytile - start_ytile) * TILE_SIZE + offset_y - self.marker_pixbuf.get_height())

        # Draw the marker at center of the map
        Gdk.cairo_set_source_pixbuf(ctx, self.marker_pixbuf, pixel_x, pixel_y)
        ctx.paint()

        # Draw coordinates as text (optional)
        ctx.select_font_face("Sans", 0, 0)
        ctx.set_font_size(14)
        ctx.set_source_rgb(0, 0, 0)  # Black text
        coord_text = f"Lat: {self.center_lat:.5f}, Lon: {self.center_lon:.5f}"
        ctx.move_to(10, 20)
        ctx.show_text(coord_text)

        # Draw clicked marker and coordinates
        if self.clicked_latlon and hasattr(self, 'marker_pixbuf'):
            lat, lon = self.clicked_latlon
            xtile, ytile = self.deg2num(lat, lon, self.zoom)
            pixel_x = round((xtile - start_x) * TILE_SIZE + offset_x - self.marker_pixbuf.get_width() / 2)
            pixel_y = round((ytile - start_y) * TILE_SIZE + offset_y - self.marker_pixbuf.get_height())

            Gdk.cairo_set_source_pixbuf(ctx, self.marker_pixbuf, pixel_x, pixel_y)
            ctx.paint()

            ctx.set_source_rgb(0, 0, 0)
            ctx.move_to(pixel_x, pixel_y - 5)
            ctx.show_text(f"{lat:.5f}, {lon:.5f}")


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