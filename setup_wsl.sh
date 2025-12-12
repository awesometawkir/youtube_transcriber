#!/bin/bash

# Exit on error
set -e

PROJECT_DIR="/mnt/d/project/youtube"
VENV_DIR="$PROJECT_DIR/.venv"

echo "Starting WSL Setup for Django Project..."

# Update and install system dependencies
echo "Updating system packages..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip

# Navigate to project directory
cd "$PROJECT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Activate venv and install dependencies
echo "Installing Python dependencies..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

# Setup Systemd Service
echo "Configuring Systemd Service..."
SERVICE_FILE="django_app.service"
SYSTEMD_PATH="/etc/systemd/system/$SERVICE_FILE"

# Copy service file
if [ -f "$SERVICE_FILE" ]; then
    sudo cp "$SERVICE_FILE" "$SYSTEMD_PATH"
    echo "Service file copied to $SYSTEMD_PATH"
else
    echo "Error: $SERVICE_FILE not found in $PROJECT_DIR"
    exit 1
fi

# Reload systemd and enable service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting service..."
sudo systemctl enable $SERVICE_FILE
sudo systemctl restart $SERVICE_FILE

echo "Checking service status..."
sudo systemctl status $SERVICE_FILE --no-pager

echo "Setup Complete! The app should be running at http://localhost:8010"
