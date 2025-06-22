#!/bin/bash

set -e

# --- Step 1: Check input ---
if [ -z "$1" ]; then
  echo "Usage: $0 <S57_FILE.000>"
  exit 1
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: File not found: $INPUT_FILE"
  exit 2
fi

# --- Step 2: Setup ---
BASENAME=$(basename "$INPUT_FILE" .000)
OUTPUT_DIR="${BASENAME}_geojson"
mkdir -p "$OUTPUT_DIR"

echo "Input file: $INPUT_FILE"
echo "Output directory: $OUTPUT_DIR"

# --- Step 3: Get all layer names ---
echo "Reading layer names..."
layers=$(ogrinfo -ro -q "$INPUT_FILE" | sed -n 's/^[0-9]\+:[[:space:]]\+\([^()]\+\).*$/\1/p' | awk '{$1=$1};1')

if [ -z "$layers" ]; then
  echo "Warning: No layers found in file."
  exit 3
fi

echo "Found layers:"
echo "$layers"

# --- Step 4: Loop and export each layer ---
for layer in $layers; do
  echo "Processing layer: $layer"

  RAW_FILE="$OUTPUT_DIR/$layer.raw.json"
  FINAL_FILE="$OUTPUT_DIR/$layer.geojson"

  # Extract layer
  ogr2ogr -f GeoJSON "$RAW_FILE" "$INPUT_FILE" "$layer"

  # Format JSON
  jq . "$RAW_FILE" > "$FINAL_FILE"

  # Clean up
  rm -f "$RAW_FILE"

  echo "Saved: $FINAL_FILE"
done

echo "Export completed. Output directory: $OUTPUT_DIR"
