#!/bin/bash

# Setup script for Plaid Link integration project

echo "🚀 Setting up Plaid Link Integration Project"
echo "=============================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo "📚 Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Setup environment file
if [ ! -f .env ]; then
    echo "🔐 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env with your Plaid credentials!"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Plaid credentials (PLAID_CLIENT_ID and PLAID_SECRET)"
echo "2. Run: python app.py"
echo "3. Visit: http://localhost:5000"
echo ""
