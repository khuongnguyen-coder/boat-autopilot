from views.map.map_layer.achare_layer import ACHARELayer

LAYER_CLASS_MAP = {
    "ACHARE": {
        "class": ACHARELayer,
        "line_color": (0.0, 0.0, 0.5),      # Dark blue stroke
        "width": 1,
        "fill_color": (0.5, 1.0, 1.0),      # Light cyan fill
        "fill_opacity": 0.1                 # Semi-transparent
    }
}
