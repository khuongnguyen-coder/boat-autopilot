#!/bin/bash

# #!/bin/bash
# source ./export_s57_to_geojson.sh
# ENC_FILE="path/to/V25AT001.000"
# OUT_DIR="geojson_output"
# export_s57_to_geojson "$ENC_FILE" "$OUT_DIR"

# Function: Export all layers of an S57 ENC file to individual GeoJSON files
# Usage: export_s57_to_geojson <S57_FILE.000> <output_directory>
export_s57_to_geojson() {
    local INPUT_FILE="$1"
    local OUTPUT_DIR="$2"

    if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_DIR" ]; then
        echo "Usage: export_s57_to_geojson <S57_FILE.000> <output_directory>"
        return 1
    fi

    if [ ! -f "$INPUT_FILE" ]; then
        echo "Error: File not found: $INPUT_FILE"
        return 2
    fi

    mkdir -p "$OUTPUT_DIR"
    echo "Input file: $INPUT_FILE"
    echo "Output directory: $OUTPUT_DIR"

    echo "Reading layer names..."
    local layers
    layers=$(ogrinfo -ro -q "$INPUT_FILE" | sed -n 's/^[0-9]\+:[[:space:]]\+\([^()]\+\).*$/\1/p' | awk '{$1=$1};1')

    if [ -z "$layers" ]; then
        echo "Warning: No layers found in file."
        return 3
    fi

    echo "Found layers:"
    echo "$layers"
    echo

    for layer in $layers; do
        echo "Processing layer: $layer"
        local RAW_FILE="$OUTPUT_DIR/$layer.raw.json"
        local FINAL_FILE="$OUTPUT_DIR/$layer.geojson"

        # Extract layer
        ogr2ogr -f GeoJSON "$RAW_FILE" "$INPUT_FILE" "$layer"

        # Format JSON
        jq . "$RAW_FILE" > "$FINAL_FILE"

        # Clean up
        rm -f "$RAW_FILE"
        echo "Saved: $FINAL_FILE"
    done

    echo
    echo "✅ Export completed. Output directory: $OUTPUT_DIR"
    return 0
}

# --- Main entry point for standalone use ---
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ "$#" -ne 2 ]; then
        echo "Usage: $0 <S57_FILE.000> <output_directory>"
        exit 1
    fi

    export_s57_to_geojson "$1" "$2"
    exit $?
fi
