#!/bin/bash

# ------------------------------------------------------------------------------
# VNEST Autopilot Launcher Script
# Runs resource build steps and launches the main Python application.
# ------------------------------------------------------------------------------

set -e  # ⛔ Exit immediately if any command fails

# 📂 Change to the directory where this script is located
cd "$(dirname "$0")"

# ------------------------------------------------------------------------------
# Parse arguments
# ------------------------------------------------------------------------------
USE_VALGRIND=false
for arg in "$@"; do
    case $arg in
        -v|--valgrind)
            USE_VALGRIND=true
            shift
            ;;
    esac
done

# ------------------------------------------------------------------------------
# 🔧 Step 1: Normalize Glade Paths
# ------------------------------------------------------------------------------
echo "📦 Step 1: Normalizing Glade paths..."
./scripts/normalize_paths.sh ui/main.glade

# ------------------------------------------------------------------------------
# 🛠️ Step 2: Update GResource
# ------------------------------------------------------------------------------
echo "📦 Step 2: Updating GResource..."
./scripts/update_resources.sh resources.xml

# ------------------------------------------------------------------------------
# 🧪 Step 3: Verify GResource Contents
# ------------------------------------------------------------------------------
echo "📦 Step 3: Verifying resources..."
gresource list resources.gresource
echo ""

# ------------------------------------------------------------------------------
# 🚀 Step 4: Launch VNEST Autopilot App
# ------------------------------------------------------------------------------
if [ "$USE_VALGRIND" = true ]; then
    echo "🚀 Step 4: Launching VNEST Autopilot under Valgrind..."
    G_DEBUG=gc-friendly G_SLICE=always-malloc \
    valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes \
             --log-file=valgrind.log \
             python3 main.py
else
    echo "🚀 Step 4: Launching VNEST Autopilot..."
    python3 main.py
fi
echo ""
