@echo off
echo ========================================
echo ChatSift Backend Setup and Run Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

echo Running database migrations...
python manage.py migrate
echo.

echo Creating superuser (if needed)...
echo You can skip this if you already have a superuser
python manage.py createsuperuser --noinput --email admin@chatsift.com --username admin 2>nul
echo.

echo ========================================
echo Starting Django development server...
echo Backend will be available at: http://localhost:8000
echo Admin panel at: http://localhost:8000/admin
echo API endpoints at: http://localhost:8000/api/v1/
echo ========================================
echo.
python manage.py runserver

@REM Made with Bob
