from views.map.map_layer.achare_layer import ACHARELayer
from views.map.map_layer.achbrt_layer import ACHBRTLayer
from views.map.map_layer.airare_layer import AIRARELayer

LAYER_CLASS_MAP = {
    "ACHARE": {
        "class": ACHARELayer,
        "line_color": (0.0, 0.0, 0.5),      # Dark blue stroke
        "width": 1,
        "fill_color": (0.5, 1.0, 1.0),      # Light cyan fill
        "fill_opacity": 0.1                 # Semi-transparent
    },

    "ACHBRT": {
        "class": ACHBRTLayer,
        "line_color": (0.0, 0.0, 0.5),      # Dark blue for depth contour lines
        "width": 1,
        "fill_color": (0.7, 0.85, 1.0),     # Light blue for shallow water areas
        "fill_opacity": 0.3                  # Semi-transparent to show map underneath
    },

    "AIRARE": {
        "class": AIRARELayer,
        "line_color": (1.0, 0.0, 0.0),      # Red boundary lines for restricted airspace
        "width": 1,
        "fill_color": (1.0, 0.8, 0.8),      # Light red/pink fill
        "fill_opacity": 0.3                  # Semi-transparent
    }
}
