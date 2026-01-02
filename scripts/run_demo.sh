#!/bin/bash

# Universal-SciAgent Quick Start Script

echo "======================================"
echo "Universal-SciAgent Quick Start"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please copy .env.example to .env and set your API keys:"
    echo "  cp .env.example .env"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10+ required (found: $python_version)"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Run example
echo ""
echo "Running examples..."
echo ""

python3 examples/simple_example.py

echo ""
echo "======================================"
echo "Demo completed!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Open notebooks/demo.ipynb in Jupyter"
echo "  2. Explore config/domains/ for domain configurations"
echo "  3. Read README.md for more information"
echo ""

