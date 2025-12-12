#!/bin/bash

# Navigate to project directory
# Ensure this matches the mounted path in WSL
PROJECT_DIR="/mnt/d/project/youtube"
cd "$PROJECT_DIR" || exit

echo "🚀 Starting Youtube App (WSL)..."

# Check if venv exists
if [ ! -d ".venv_wsl" ]; then
    echo "📦 Creating Linux virtual environment..."
    python3 -m venv .venv_wsl
    
    echo "🔌 Activating..."
    source .venv_wsl/bin/activate
    
    echo "⬇️ Installing dependencies..."
    pip install -r requirements.txt
    
    # Ensure static ffmpeg for linux if needed, usually apt is better but let's try pip package first
    # pip install static-ffmpeg 
else
    source .venv_wsl/bin/activate
fi

# Run Migrations
python manage.py migrate

# Start Server
# 0.0.0.0 allows external access (mobile)
echo "✅ Server starting on port 8010..."
python manage.py runserver 0.0.0.0:8010
