@echo off
REM MedAssist Docker Management Commands

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="test" goto test
if "%1"=="clean" goto clean

echo Usage: docker-commands.bat [start^|stop^|restart^|logs^|status^|test^|clean]
goto end

:start
echo Starting MedAssist container...
docker run -d -p 8000:8000 --env-file .env --name medassist-container medassist:latest
echo MedAssist started at http://localhost:8000
goto end

:stop
echo Stopping MedAssist container...
docker stop medassist-container
docker rm medassist-container
echo MedAssist stopped
goto end

:restart
echo Restarting MedAssist...
call :stop
timeout /t 2 /nobreak >nul
call :start
goto end

:logs
echo MedAssist logs:
docker logs -f medassist-container
goto end

:status
echo MedAssist status:
docker ps --filter name=medassist-container
echo.
echo Health check:
curl -s http://localhost:8000/health
goto end

:test
echo Testing MedAssist API...
curl -s -X POST http://localhost:8000/test -H "Content-Type: application/json" -d "{}"
goto end

:clean
echo Cleaning up MedAssist resources...
docker stop medassist-container 2>nul
docker rm medassist-container 2>nul
docker rmi medassist:latest 2>nul
echo Cleanup complete
goto end

:end