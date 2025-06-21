#!/bin/bash

set -e  # ⛔ Stop on first error
trap 'echo "❌ Error occurred. Exiting."; exit 1' ERR

RESOURCE_XML="$1"
RESOURCE_FILE="resources.gresource"
ICON_DIR="ui/assets/icons"
MAP_DIR="ui/assets/map"
CSS_DIR="ui/css"
GLADE_FILE="ui/main.glade"

ASSETS_PREFIX="/vn/vnest/autopilot"
DESIGN_PREFIX="/vn/vnest/autopilot"

echo ""
echo "🔧 Building $RESOURCE_XML and compiling $RESOURCE_FILE ..."
echo ""

# 🔍 Check if XML file is given
if [[ -z "$RESOURCE_XML" ]]; then
    echo "❌ Usage: $0 <path/to/resources.xml>"
    exit 1
fi

# 🛑 Check if XML file exists
if [[ ! -f "$RESOURCE_XML" ]]; then
    echo "❌ File not found: $RESOURCE_XML"
    exit 1
fi

# 💾 Backup
DIR=$(dirname "$RESOURCE_XML")
BASE=$(basename "$RESOURCE_XML")
cp "$RESOURCE_XML" "$DIR/.${BASE}.bak"

# 🔁 Generate <file> entries
make_file_entries() {
    local DIR="$1"
    find "$DIR" -type f | sort | sed 's/^/    <file>/' | sed 's/$/<\/file>/'
}

ICON_FILES=$(make_file_entries "$ICON_DIR")
MAP_FILES=$(make_file_entries "$MAP_DIR")
CSS_FILES=$(make_file_entries "$CSS_DIR")

# ✅ Check UI file
if [[ ! -f "$GLADE_FILE" ]]; then
    echo "❌ UI file not found: $GLADE_FILE"
    exit 1
fi
GLADE_ENTRY="    <file>$GLADE_FILE</file>"

# 🛠 Build XML
cat > "$RESOURCE_XML" <<EOF
<gresources>
  <gresource prefix="$ASSETS_PREFIX">
$ICON_FILES
$MAP_FILES
$CSS_FILES
  </gresource>

  <gresource prefix="$DESIGN_PREFIX">
$GLADE_ENTRY
  </gresource>
</gresources>
EOF

echo "✅ Rebuilt $RESOURCE_XML with:"
echo "  - $(echo "$ICON_FILES" | grep -c '<file>') icon file(s)"
echo "  - $(echo "$MAP_FILES" | grep -c '<file>') map file(s)"
echo "  - 1 UI file: $GLADE_FILE"
echo ""

# 🚀 Compile to GResource
glib-compile-resources "$RESOURCE_XML" --target="$RESOURCE_FILE" --sourcedir=.

echo "✅ Done: $RESOURCE_FILE generated"
echo ""
