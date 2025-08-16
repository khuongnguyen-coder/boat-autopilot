"""
config.py - Global configuration settings for Vnest Autopilot.

This module stores application-wide constants and feature flags
used across the project. Centralizing configuration helps maintain
cleaner code and easier maintenance.

Settings:
    ENABLE_FEATURE_TILE_DOWNLOAD_RUNTIME (bool): 
        Enable/disable runtime tile downloading feature.
        Default = False

    VNEST_AUTOPILOT_DATABASE_PATH (str): 
        Path to the ENC metadata database directory.
        Default = "database"

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

# ********************************************************************************************
# [Feature Flags]
ENABLE_FEATURE_TILE_DOWNLOAD_RUNTIME = False
# ********************************************************************************************

# ********************************************************************************************
# [Database Settings]
VNEST_AUTOPILOT_DATABASE_PATH = "database"
# ********************************************************************************************
