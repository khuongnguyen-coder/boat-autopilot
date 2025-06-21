#!/bin/bash
echo "🧹 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
echo "✅ Done."

