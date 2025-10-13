@echo off
REM Environment switcher script for adCTF (Windows)

if "%1"=="local" goto local
if "%1"=="docker" goto docker
goto usage

:local
echo 🔄 Switching to LOCAL development environment...
copy .env.local .env >nul
echo ✅ Environment switched to LOCAL
echo 📝 Database will connect to: localhost:3306
echo 📝 Redis will connect to: localhost:6379
echo.
echo You can now run:
echo   python init_db.py
echo   python run.py
goto end

:docker
echo 🔄 Switching to DOCKER environment...
copy .env.docker .env >nul
echo ✅ Environment switched to DOCKER
echo 📝 Database will connect to: db:3306
echo 📝 Redis will connect to: redis:6379
echo.
echo You can now run:
echo   docker compose up -d
goto end

:usage
echo Usage: %0 {local^|docker}
echo.
echo Commands:
echo   %0 local   - Switch to local development (connects to localhost)
echo   %0 docker  - Switch to Docker environment (connects to service names)
echo.
echo Current environment:
findstr /C:"localhost" .env >nul 2>&1
if %errorlevel%==0 (
    echo   📍 LOCAL (connects to localhost)
) else (
    findstr /C:"@db:" .env >nul 2>&1
    if %errorlevel%==0 (
        echo   📍 DOCKER (connects to service names)
    ) else (
        echo   ❓ UNKNOWN or no .env file found
    )
)
exit /b 1

:end