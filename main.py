"""
main.py - Application entry point for Vnest Autopilot.

This script ensures the working directory is set correctly and 
launches the VnestAutopilot GTK application.

Execution:
    python main.py

Responsibilities:
    - Set current working directory to the project root.
    - Import and instantiate the main application class.
    - Run the GTK application loop.

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import os

# ********************************************************************************************
# [Setup Working Directory]
# Make sure the current working directory is the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# ********************************************************************************************

# ********************************************************************************************
# [Application Entry]
from app import VnestAutopilot

if __name__ == "__main__":
    app = VnestAutopilot()
    app.run()
# ********************************************************************************************
