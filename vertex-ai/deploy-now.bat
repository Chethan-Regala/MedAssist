@echo off
echo ========================================
echo MedAssist Vertex AI Deployment
echo ========================================

REM Check if gcloud is installed
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Google Cloud SDK not found!
    echo.
    echo Please install Google Cloud SDK first:
    echo 1. Go to: https://cloud.google.com/sdk/docs/install
    echo 2. Download and install Google Cloud SDK
    echo 3. Restart this script
    echo.
    pause
    exit /b 1
)

echo ✓ Google Cloud SDK found

REM Get project ID
set /p PROJECT_ID="Enter your Google Cloud Project ID: "
if "%PROJECT_ID%"=="" (
    echo ERROR: Project ID cannot be empty
    pause
    exit /b 1
)

REM Get Gemini API Key
set /p GEMINI_API_KEY="Enter your Gemini API Key: "
if "%GEMINI_API_KEY%"=="" (
    echo ERROR: Gemini API Key cannot be empty
    pause
    exit /b 1
)

echo.
echo Using Project ID: %PROJECT_ID%
echo.

REM Set project
echo Setting up project...
gcloud config set project %PROJECT_ID%

REM Enable APIs
echo Enabling required APIs...
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

REM Build and deploy
echo Building container image...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/medassist .

echo Deploying to Cloud Run...
gcloud run deploy medassist-api --image gcr.io/%PROJECT_ID%/medassist --platform managed --region us-central1 --allow-unauthenticated --port 8000 --memory 2Gi --cpu 1 --set-env-vars "GEMINI_API_KEY=%GEMINI_API_KEY%,GEMINI_MODEL=gemini-2.5-flash"

REM Get URL
echo Getting Cloud Run URL...
for /f "tokens=*" %%i in ('gcloud run services describe medassist-api --region us-central1 --format "value(status.url)" 2^>nul') do set API_URL=%%i

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo Cloud Run API: %API_URL%
echo.
echo Next steps:
echo 1. Go to: https://console.cloud.google.com/ai/agents
echo 2. Create new Vertex AI Agent
echo 3. Use API URL: %API_URL%
echo 4. Import tools from agent-tools.json
echo ========================================
echo.

REM Test API
echo Testing API...
curl -X POST "%API_URL%/test" -H "Content-Type: application/json" -d "{}"

echo.
echo Press any key to open Vertex AI console...
pause >nul
start https://console.cloud.google.com/ai/agents