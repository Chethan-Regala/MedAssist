# Manual Vertex AI Deployment Steps

## Prerequisites Setup

### 1. Install Google Cloud SDK
```bash
# Download and install from: https://cloud.google.com/sdk/docs/install
# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

### 2. Get Your Project ID
**See `get-project-id.md` for detailed instructions**

**Quick steps**:
1. Go to https://console.cloud.google.com
2. Create new project or select existing one
3. Copy the Project ID (format: `project-name-123456`)

### 3. Initialize gcloud
```bash
gcloud init
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

## Step-by-Step Deployment

### Step 1: Enable Required APIs
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com  
gcloud services enable run.googleapis.com
gcloud services enable dialogflow.googleapis.com
```

### Step 2: Build and Push Container
```bash
# From your MedAssist root directory
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/medassist .
```

### Step 3: Deploy to Cloud Run
```bash
gcloud run deploy medassist-api \
  --image gcr.io/YOUR_PROJECT_ID/medassist \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars "GEMINI_API_KEY=YOUR_GEMINI_API_KEY,GEMINI_MODEL=gemini-2.5-flash,LOG_LEVEL=INFO"
```

### Step 4: Get Cloud Run URL
```bash
gcloud run services describe medassist-api --region us-central1 --format "value(status.url)"
```

### Step 5: Create Vertex AI Agent

1. Go to [Vertex AI Agent Builder Console](https://console.cloud.google.com/ai/agents)

2. Click "Create Agent"

3. Configure Agent:
   - **Name**: MedAssist Healthcare AI
   - **Description**: Multi-agent healthcare assistant
   - **Language**: English
   - **Time Zone**: UTC

4. Add System Instructions:
```
You are MedAssist, a professional healthcare AI assistant. You help users with:
1. Medical symptom triage and recommendations
2. Medication safety and interaction checking  
3. Health monitoring and reminders

Always prioritize safety and recommend professional medical care when appropriate.
Use the available tools to provide accurate, evidence-based responses.
```

5. Add Tools (use your Cloud Run URL):
   - **Triage Tool**: `POST {CLOUD_RUN_URL}/triage`
   - **Medication Tool**: `POST {CLOUD_RUN_URL}/medications/check`
   - **Health Assessment**: `POST {CLOUD_RUN_URL}/health-assessment`

### Step 6: Test Deployment
```bash
# Test Cloud Run API
curl -X POST "YOUR_CLOUD_RUN_URL/test" -H "Content-Type: application/json" -d "{}"

# Test Vertex AI Agent in console
```

## Manual Configuration Commands

Replace `YOUR_PROJECT_ID` and `YOUR_GEMINI_API_KEY` with your actual values:

```bash
export PROJECT_ID="your-project-id"
export GEMINI_API_KEY="your-gemini-api-key"

# Enable APIs
gcloud services enable aiplatform.googleapis.com cloudbuild.googleapis.com run.googleapis.com

# Build image
gcloud builds submit --tag gcr.io/$PROJECT_ID/medassist .

# Deploy to Cloud Run
gcloud run deploy medassist-api \
  --image gcr.io/$PROJECT_ID/medassist \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY,GEMINI_MODEL=gemini-2.5-flash"

# Get URL
gcloud run services describe medassist-api --region us-central1 --format "value(status.url)"
```

## Verification Steps

1. **API Health Check**:
```bash
curl https://YOUR_CLOUD_RUN_URL/health
```

2. **Test Triage**:
```bash
curl -X POST "https://YOUR_CLOUD_RUN_URL/triage" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","symptoms":"headache","context":"mild"}'
```

3. **Vertex AI Agent**: Test in the console interface

## Troubleshooting

- **Build fails**: Check Dockerfile and requirements.txt
- **Deploy fails**: Verify environment variables
- **Agent not responding**: Check Cloud Run logs
- **Tools not working**: Verify OpenAPI spec URLs