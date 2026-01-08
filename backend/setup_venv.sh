#!/bin/bash
# Setup Python virtual environment for ReconVault backend
# This script recreates the venv to fix cross-platform issues

set -e

echo "🔧 Setting up ReconVault backend virtual environment..."

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing existing venv..."
    rm -rf venv
fi

# Create new virtual environment
echo "✨ Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

echo "✅ Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate later, run:"
echo "  deactivate"
