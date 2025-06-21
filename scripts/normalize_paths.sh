#!/bin/bash
echo ""

INPUT_FILE="$1"

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "❌ File not found: $INPUT_FILE"
    exit 1
fi

# Backup original
DIR=$(dirname "$INPUT_FILE")
BASE=$(basename "$INPUT_FILE")
cp "$INPUT_FILE" "$DIR/.${BASE}.bak"

# Normalize any '../assets/...' to 'assets/...'
sed -i 's|\.\./assets/|assets/|g' "$INPUT_FILE"

echo "✅ Normalized Glade paths in $INPUT_FILE"
echo ""