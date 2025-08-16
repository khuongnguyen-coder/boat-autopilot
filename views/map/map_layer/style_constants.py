"""
style_constants.py

This module defines reusable style constants for map layers.
It is intended to centralize visual styling (e.g. line styles, dash patterns),
so they can be used consistently across all layers without creating circular imports.

Usage:
    from views.map.map_layer.style_constants import LINE_STYLE_PATTERNS

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

# -----------------------------------------------------------------------------
# Predefined line style dash patterns for Cairo
# Each entry maps a style name (string) to a dash pattern (list of floats).
#
# The dash pattern format follows Cairo's `ctx.set_dash(pattern)`:
#   - An empty list [] means a solid line.
#   - [dash_length, gap_length] defines repeating dash/gap lengths in pixels.
#   - More complex patterns (e.g. [dash, gap, dot, gap]) can also be defined.
# -----------------------------------------------------------------------------
LINE_STYLE_PATTERNS = {
    "solid":  [],             # Continuous solid line
    "dashed": [10.0, 5.0],    # 10px dash, 5px gap
    "dotted": [2.0, 4.0],     # 2px dot, 4px gap
    # Example of a dash-dot style (optional extra):
    # "dashdot": [10.0, 4.0, 2.0, 4.0]
}
