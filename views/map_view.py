import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from views.map.map_visualize import MapVisualize

from utils.log import utils_log_get_logger
LOG_INFO  = utils_log_get_logger("map_view")["info"]
LOG_DEBUG = utils_log_get_logger("map_view")["debug"]
LOG_WARN  = utils_log_get_logger("map_view")["warn"]
LOG_ERR   = utils_log_get_logger("map_view")["err"]

BTN_SIZE = 64
BTN_GAP = 10
MARGIN_BASE = 10

class MapView(Gtk.Overlay):

    # ********************************************************************************************
    # [INIT]
    def __init__(self, _map_visualize):

        """
        Initialize the map view with overlays for zooming, panning, and location control.
        
        Args:
            _map_visualize (MapVisualize): The map widget to display and control.
        """
            
        super().__init__()

        # ----------------------------------------------------------------------------------------
        # [Map view]
        self.map_visualize = _map_visualize
        self.add(self.map_visualize)
        # ----------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------
        # [Button: zoom in]
        self.btn_zoom_in = Gtk.Button()
        self.btn_zoom_in.set_size_request(BTN_SIZE, BTN_SIZE)
        # Load the zoom in icon from resources
        image = Gtk.Image.new_from_resource("/vn/vnest/autopilot/ui/assets/map/map_zoon_in.png")
        self.btn_zoom_in.set_image(image)
        self.btn_zoom_in.set_always_show_image(True)
        self.btn_zoom_in.set_relief(Gtk.ReliefStyle.NONE)  # Optional for flat look
        # Set margins and alignment
        self.btn_zoom_in.set_margin_bottom(BTN_SIZE*2 + BTN_GAP*2 + MARGIN_BASE)
        self.btn_zoom_in.set_margin_end(10)
        self.btn_zoom_in.set_halign(Gtk.Align.END)
        self.btn_zoom_in.set_valign(Gtk.Align.END)
        self.btn_zoom_in.set_tooltip_text("Zoom In")
        self.btn_zoom_in.set_can_focus(False)
        self.btn_zoom_in.set_focus_on_click(False)
        # Add a CSS class for styling
        self.btn_zoom_in.get_style_context().add_class("map-button")
        # Connect the button click event to the zoom in method
        self.btn_zoom_in.connect("clicked", self.on_zoom_in)
        self.add_overlay(self.btn_zoom_in)

        # ----------------------------------------------------------------------------------------
        # [Button: zoom out]
        self.btn_zoom_out = Gtk.Button()
        self.btn_zoom_out.set_size_request(BTN_SIZE, BTN_SIZE)
        # Load the zoom out icon from resources
        image = Gtk.Image.new_from_resource("/vn/vnest/autopilot/ui/assets/map/map_zoon_out.png")
        self.btn_zoom_out.set_image(image)
        self.btn_zoom_out.set_always_show_image(True)
        self.btn_zoom_out.set_relief(Gtk.ReliefStyle.NONE)  # Optional for flat look
        # Set margins and alignment
        self.btn_zoom_out.set_margin_bottom(10)
        self.btn_zoom_out.set_margin_end(10)
        self.btn_zoom_out.set_halign(Gtk.Align.END)
        self.btn_zoom_out.set_valign(Gtk.Align.END)
        self.btn_zoom_out.set_tooltip_text("Zoom Out")
        self.btn_zoom_out.set_can_focus(False)
        self.btn_zoom_out.set_focus_on_click(False)
        # Add a CSS class for styling
        self.btn_zoom_out.get_style_context().add_class("map-button")
        # Connect the button click event to the zoom out method
        self.btn_zoom_out.connect("clicked", self.on_zoom_out)
        self.add_overlay(self.btn_zoom_out)
        # ----------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------
        # [Button: My location]
        self.btn_my_location = Gtk.Button()
        self.btn_my_location.set_size_request(BTN_SIZE, BTN_SIZE)
        # Load the my location icon from resources
        image = Gtk.Image.new_from_resource("/vn/vnest/autopilot/ui/assets/map/map_my_location.png")
        self.btn_my_location.set_image(image)
        self.btn_my_location.set_always_show_image(True)
        self.btn_my_location.set_relief(Gtk.ReliefStyle.NONE)  # Optional for flat look
        # Set margins and alignment
        self.btn_my_location.set_margin_bottom(BTN_SIZE + BTN_GAP + MARGIN_BASE)
        self.btn_my_location.set_margin_end(10)
        self.btn_my_location.set_halign(Gtk.Align.END)
        self.btn_my_location.set_valign(Gtk.Align.END)
        self.btn_my_location.set_tooltip_text("My Location")
        self.btn_my_location.set_can_focus(False)
        self.btn_my_location.set_focus_on_click(False)
        # Add a CSS class for styling
        self.btn_my_location.get_style_context().add_class("map-button")
        # Connect the button click event to the my location method
        self.btn_my_location.connect("clicked", self.on_my_location)
        self.add_overlay(self.btn_my_location)
        # ----------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------
        # [Button: Go up]
        self.btn_up = self.make_arrow_button("up", "Pan Up", self.on_pan_up, BTN_GAP, 258)
        img = Gtk.Image.new_from_resource("/vn/vnest/autopilot/ui/assets/map/map_arrow_up.png")
        self.btn_up.set_image(img)
        self.btn_up.set_always_show_image(True)
        # ----------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------
        # [Button: Go down]
        self.btn_down = self.make_arrow_button("down", "Pan Down", self.on_pan_down, BTN_GAP, 174)
        img = Gtk.Image.new_from_resource("/vn/vnest/autopilot/ui/assets/map/map_arrow_down.png")
        self.btn_down.set_image(img)
        self.btn_down.set_always_show_image(True)
        # ----------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------
        # [Button: Go left]
        self.btn_left = self.make_arrow_button("left", "Pan Left", self.on_pan_left, BTN_GAP, 332)
        img = Gtk.Image.new_from_resource("/vn/vnest/autopilot/ui/assets/map/map_arrow_left.png")
        self.btn_left.set_image(img)
        self.btn_left.set_always_show_image(True)
        # ----------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------
        # [Button: Go right]
        self.btn_right = self.make_arrow_button("right", "Pan Right", self.on_pan_right, BTN_GAP, 94)
        img = Gtk.Image.new_from_resource("/vn/vnest/autopilot/ui/assets/map/map_arrow_right.png")
        self.btn_right.set_image(img)
        self.btn_right.set_always_show_image(True)
        # ----------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------
        # [Zoom/Center Info Label]
        self.info_label = Gtk.Label()
        self.info_label.set_halign(Gtk.Align.START)
        self.info_label.set_valign(Gtk.Align.END)
        self.info_label.set_margin_start(MARGIN_BASE)
        self.info_label.set_margin_top(MARGIN_BASE)
        self.info_label.get_style_context().add_class("map-info-label")
        self.add_overlay(self.info_label)
        # if map_visualize has signals/events for view changes, connect them:
        self.map_visualize.connect("view-changed", lambda *a: self.update_info_label())
        # ----------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------
        # Initial update
        self.update_info_label()
        # # Start simulation (e.g. in your main view init)
        # self.map_visualize.curr_gps_location_sim_start(interval_ms=1000)
        # ----------------------------------------------------------------------------------------
    # ********************************************************************************************
    
    # ********************************************************************************************
    # [STOP]
    def stop(self):
        # Stop simulation later if needed
        # self.map_visualize.curr_gps_location_sim_stop()
        LOG_DEBUG(f"[STOP] Map view stopped.")
    # ********************************************************************************************

    # ********************************************************************************************
    # [Callback handler]
    def make_arrow_button(self, arrow_type, tooltip, callback, margin_bottom, margin_end):
        btn = Gtk.Button()
        btn.set_size_request(BTN_SIZE, BTN_SIZE)
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.set_tooltip_text(tooltip)
        btn.set_can_focus(False)
        btn.set_focus_on_click(False)
        btn.set_halign(Gtk.Align.END)
        btn.set_valign(Gtk.Align.END)
        btn.set_margin_bottom(margin_bottom)
        btn.set_margin_end(margin_end)
        btn.get_style_context().add_class("map-button")
        btn.connect("clicked", callback)
        self.add_overlay(btn)
        return btn

    def on_zoom_in(self, button):
        self.map_visualize.zoom_level_increase()

    def on_zoom_out(self, button):
        self.map_visualize.zoom_level_decrease()
    
    def on_pan_up(self, button):
        self.map_visualize.pan_handler_up()

    def on_pan_down(self, button):
        self.map_visualize.pan_handler_down()

    def on_pan_left(self, button):
        self.map_visualize.pan_handler_left()

    def on_pan_right(self, button):
        self.map_visualize.pan_handler_right()

    def on_my_location(self, button):
        self.map_visualize.curr_gps_location_force()
    
    def update_info_label(self):
        zoom = self.map_visualize.zoom_level_get_curr_value()
        center_lat, center_lon = self.map_visualize.curr_center_location_get()
        self.info_label.set_text(f"[{center_lat:.6f}, {center_lon:.6f}] [{zoom}]")

    # ********************************************************************************************
