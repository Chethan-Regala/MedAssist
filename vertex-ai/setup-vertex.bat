@echo off
echo Setting up Vertex AI deployment for MedAssist...

REM Check if gcloud is installed
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Google Cloud SDK not found
    echo Please install gcloud CLI from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Check if project is set
for /f "tokens=*" %%i in ('gcloud config get-value project 2^>nul') do set PROJECT_ID=%%i
if "%PROJECT_ID%"=="" (
    echo Error: No GCP project set
    echo Please run: gcloud config set project YOUR_PROJECT_ID
    pause
    exit /b 1
)

echo Using project: %PROJECT_ID%

REM Enable required APIs
echo Enabling required APIs...
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable dialogflow.googleapis.com

REM Set environment variables
set /p GEMINI_API_KEY="Enter your Gemini API Key: "

REM Deploy using Cloud Build
echo Building and deploying to Cloud Run...
gcloud builds submit --config=cloudbuild.yaml --substitutions=_GEMINI_API_KEY=%GEMINI_API_KEY%

REM Get Cloud Run URL
for /f "tokens=*" %%i in ('gcloud run services describe medassist-api --region us-central1 --format "value(status.url)" 2^>nul') do set API_URL=%%i

echo.
echo ========================================
echo Vertex AI Deployment Complete!
echo ========================================
echo API Backend: %API_URL%
echo Agent Console: https://console.cloud.google.com/ai/agents
echo ========================================
echo.
echo Next steps:
echo 1. Go to Vertex AI Agent Builder console
echo 2. Create new agent using the API_URL above
echo 3. Import tools from agent-tools.json
echo 4. Configure system instructions from agent-config.yaml
echo.
pause