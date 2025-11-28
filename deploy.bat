@echo off
echo Starting MedAssist Deployment...

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed or not running
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)

REM Build and start the application
echo Building MedAssist container...
docker-compose build

echo Starting MedAssist services...
docker-compose up -d

echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps

echo.
echo ========================================
echo MedAssist Deployment Complete!
echo ========================================
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Health: http://localhost:8000/health
echo ========================================
echo.
echo Press any key to view logs...
pause >nul
docker-compose logs -f