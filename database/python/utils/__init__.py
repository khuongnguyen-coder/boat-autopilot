# utils/__init__.py

"""
utils package initializer.

This module exposes core utility functions from submodules
for easy and direct access when imported as `import utils`.
"""

# Import commonly used utility functions from submodules
from .helper import (
	get_file_size_kb,
	get_dir_size_kb
)

# Define the public API of this package
__all__ = [
	"get_file_size_kb",
	"get_dir_size_kb"
]
