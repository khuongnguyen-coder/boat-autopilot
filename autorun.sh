#!/bin/bash

# ------------------------------------------------------------------------------
# VNEST Autopilot Launcher Script
# Runs resource build steps and launches the main Python application.
# ------------------------------------------------------------------------------

set -e  # ⛔ Exit immediately if any command fails

# 📂 Change to the directory where this script is located
cd "$(dirname "$0")"

# ------------------------------------------------------------------------------
# 🔧 Step 1: Normalize Glade Paths
# This ensures the UI XML file has correct resource paths for GResource.
# ------------------------------------------------------------------------------
echo "📦 Step 1: Normalizing Glade paths..."
./scripts/normalize_paths.sh ui/main.glade

# ------------------------------------------------------------------------------
# 🛠️ Step 2: Update GResource
# Compiles the resource XML into a .gresource binary file.
# ------------------------------------------------------------------------------
echo "📦 Step 2: Updating GResource..."
./scripts/update_resources.sh resources.xml

# ------------------------------------------------------------------------------
# 🧪 Step 3: Verify GResource Contents
# Optional: list contents of the compiled resources.gresource file.
# ------------------------------------------------------------------------------
echo "📦 Step 3: Verifying resources..."
gresource list resources.gresource
echo ""
# ------------------------------------------------------------------------------
# 🚀 Step 4: Launch VNEST Autopilot App
# Starts the GTK application via main.py.
# ------------------------------------------------------------------------------
echo "🚀 Step 4: Launching VNEST Autopilot..."
python3 main.py
echo ""
