#!/bin/bash

# ElephantAI Alert System - Installation Script

echo "🐘 ElephantAI Alert System - Installation"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed. Please install pip."
    exit 1
fi

echo "Python and pip found"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Setup database
echo "Setting up database..."
python scripts/setup_database.py

# Create necessary directories
echo "Creating directories..."
mkdir -p app/static/images
mkdir -p ml/models
mkdir -p camera_simulator/sample_images

echo ""
echo "Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure your settings"
echo "2. Run: python run.py"
echo "3. Open http://localhost:5000 in your browser"
echo "4. For demo: python scripts/start_demo.py"
echo ""
echo "For Twilio SMS notifications:"
echo "- Sign up at https://www.twilio.com/try-twilio"
echo "- Get your Account SID, Auth Token, and phone number"
echo "- Add them to your .env file"
echo ""