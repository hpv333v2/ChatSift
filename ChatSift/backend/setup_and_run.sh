#!/bin/bash

echo "========================================"
echo "ChatSift Backend Setup and Run Script"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

echo "Activating virtual environment..."
source venv/bin/activate
echo ""

echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "Running database migrations..."
python manage.py migrate
echo ""

echo "Creating superuser (if needed)..."
echo "You can skip this if you already have a superuser"
python manage.py createsuperuser --noinput --email admin@chatsift.com --username admin 2>/dev/null || true
echo ""

echo "========================================"
echo "Starting Django development server..."
echo "Backend will be available at: http://localhost:8000"
echo "Admin panel at: http://localhost:8000/admin"
echo "API endpoints at: http://localhost:8000/api/v1/"
echo "========================================"
echo ""
python manage.py runserver

# Made with Bob
