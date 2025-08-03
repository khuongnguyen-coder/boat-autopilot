#!/bin/bash

# Function: Add margin to a bounding box
# Args: minx miny maxx maxy [margin_percent]
# Output: prints 4 values: padded_minx padded_miny padded_maxx padded_maxy
padding_bounding_box() {
    local MINX="$1"
    local MINY="$2"
    local MAXX="$3"
    local MAXY="$4"
    local MARGIN_PERCENT="${5:-0.02}"  # Default 2%

    local WIDTH HEIGHT MARGIN_X MARGIN_Y
    WIDTH=$(echo "$MAXX - $MINX" | bc -l)
    HEIGHT=$(echo "$MAXY - $MINY" | bc -l)
    MARGIN_X=$(echo "$WIDTH * $MARGIN_PERCENT" | bc -l)
    MARGIN_Y=$(echo "$HEIGHT * $MARGIN_PERCENT" | bc -l)

    local PADDED_MINX PADDED_MINY PADDED_MAXX PADDED_MAXY
    PADDED_MINX=$(echo "$MINX - $MARGIN_X" | bc -l)
    PADDED_MINY=$(echo "$MINY - $MARGIN_Y" | bc -l)
    PADDED_MAXX=$(echo "$MAXX + $MARGIN_X" | bc -l)
    PADDED_MAXY=$(echo "$MAXY + $MARGIN_Y" | bc -l)

    echo "$PADDED_MINX $PADDED_MINY $PADDED_MAXX $PADDED_MAXY"
}

# Function: Get largest bounding box from geometry layers in an S57 file
get_bounding_box() {
    local S57_FILE="$1"
    local DEBUG="${DEBUG:-0}"

    if [ ! -f "$S57_FILE" ]; then
        echo "File not found: $S57_FILE"
        return 2
    fi

    # Get valid geometry layer names (ignore metadata and remove layer type info)
    local LAYERS
    IFS=$'\n' read -d '' -r -a LAYERS < <(
        ogrinfo "$S57_FILE" | \
        grep "^[0-9]\+:" | \
        grep -v -E "DSID|DSSI|DSPM|CATD" | \
        sed -E 's/^[0-9]+:\s*([^[:space:]]+).*/\1/' 
    )

    if [ "$DEBUG" == "1" ]; then
        echo "Detected layers:"
        for layer in "${LAYERS[@]}"; do
            echo "  - $layer"
        done
        echo
    fi

    local MAX_AREA=0
    local MAX_LAYER=""
    local MAX_BBOX_LINE=""

    for LAYER in "${LAYERS[@]}"; do
        [ "$DEBUG" == "1" ] && echo "Processing for $LAYER ..."

        # Extract extent line
        BBOX_LINE=$(ogrinfo "$S57_FILE" "$LAYER" -al -so 2>/dev/null | awk '/Extent/ {print; exit}' | tr -d '\r' | xargs)

        [ "$DEBUG" == "1" ] && echo "BBOX_LINE = --$BBOX_LINE--"

        if [ -z "$BBOX_LINE" ]; then
            [ "$DEBUG" == "1" ] && echo "Skipping layer $LAYER (no valid extent)"
            continue
        fi

        # Extract coordinates from extent
        read -r MINX MINY MAXX MAXY <<<$(echo "$BBOX_LINE" | grep -oP '\(-?[0-9.]+, *-?[0-9.]+\)' | tr -d '(),' | xargs)

        # Validate
        if [[ -z "$MINX" || -z "$MINY" || -z "$MAXX" || -z "$MAXY" ]]; then
            [ "$DEBUG" == "1" ] && echo "Skipping layer $LAYER (invalid extent values)"
            continue
        fi

        # Calculate area
        local AREA
        AREA=$(echo "($MAXX - $MINX) * ($MAXY - $MINY)" | bc -l)

        if [ "$DEBUG" == "1" ]; then
            printf "Layer: %-20s Area: %10.8f  Extent: %s\n" "$LAYER" "$AREA" "$BBOX_LINE"
        fi

        # Update max
        if (( $(echo "$AREA > $MAX_AREA" | bc -l) )); then
            MAX_AREA="$AREA"
            MAX_LAYER="$LAYER"
            MAX_BBOX_LINE="$BBOX_LINE"
        fi
    done

    if [ -n "$MAX_LAYER" ]; then
        echo
        echo "Largest bounding box found:"
        echo "  Layer : $MAX_LAYER"
        echo "  $MAX_BBOX_LINE"

        read -r PADDED_MINX PADDED_MINY PADDED_MAXX PADDED_MAXY <<<$(padding_bounding_box "$MINX" "$MINY" "$MAXX" "$MAXY" 0.02)
        echo
        echo "Bounding box with 2% margin:"
        echo "  ($PADDED_MINX, $PADDED_MINY) - ($PADDED_MAXX, $PADDED_MAXY)"
        echo
        return 0
    else
        echo "No valid bounding box found in any layer of $S57_FILE."
        return 4
    fi
}

# --- Main entry point for standalone use ---
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ "$#" -ne 1 ]; then
        echo "Usage: $0 path_to_s57_file"
        echo "Set DEBUG=1 to show detailed output"
        exit 1
    fi

    get_bounding_box "$1"
    exit $?
fi
