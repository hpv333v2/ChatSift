@echo off
echo ========================================
echo ChatSift Frontend Demo Script
echo ========================================
echo.

echo Installing dependencies (if needed)...
call npm install --legacy-peer-deps
echo.

echo ========================================
echo Starting Expo development server...
echo.
echo The app will open in:
echo - Expo Go app on your phone (scan QR code)
echo - Web browser at: http://localhost:8081
echo - Android emulator (press 'a')
echo - iOS simulator (press 'i' - Mac only)
echo.
echo Press 'w' to open in web browser
echo ========================================
echo.

call npm start

@REM Made with Bob
