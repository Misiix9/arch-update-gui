#!/bin/bash

# Arch Update GUI - Cleanup Script
# Removes unnecessary files before pushing to GitHub

echo "======================================"
echo "  Arch Update GUI - Cleanup"
echo "======================================"
echo ""

# Files/directories to remove
CLEANUP_ITEMS=(
    ".mypy_cache"
    "__pycache__"
    "*.pyc"
    "*.pyo"
    "*.pyd"
    ".Python"
    "*.so"
    "*.egg"
    "*.egg-info"
    "dist"
    "build"
    ".pytest_cache"
    ".coverage"
    "*.log"
    "*.tmp"
    "*~"
    ".DS_Store"
    "Thumbs.db"
    "setup-github.sh"  # Remove old setup script
)

echo "The following will be removed:"
echo ""

for item in "${CLEANUP_ITEMS[@]}"; do
    if ls $item 2>/dev/null | grep -q .; then
        echo "  - $item"
    fi
done

echo ""
read -p "Continue with cleanup? (y/n): " confirm

if [[ $confirm != "y" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Cleaning up..."

for item in "${CLEANUP_ITEMS[@]}"; do
    rm -rf $item 2>/dev/null
done

# Keep only essential files
echo ""
echo "Essential files that will be kept:"
echo "  ✓ update_gui.py (main application)"
echo "  ✓ README.md (documentation)"
echo "  ✓ FEATURES.md (feature list)"
echo "  ✓ LICENSE (MIT license)"
echo "  ✓ install.sh (installer script)"
echo "  ✓ .gitignore (git ignore rules)"
echo ""

echo "Cleanup complete!"
