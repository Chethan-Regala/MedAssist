# MedAssist Vertex AI Deployment

Deploy your MedAssist multi-agent system to Google Cloud Vertex AI Agent Engine.

## Prerequisites

1. **Google Cloud SDK**: Install from https://cloud.google.com/sdk/docs/install
2. **GCP Project**: Set up a Google Cloud project with billing enabled
3. **Gemini API Key**: Your existing Gemini API key

## Quick Deployment

### Option 1: Automated Setup (Windows)
```bash
cd vertex-ai
setup-vertex.bat
```

### Option 2: Manual Setup

1. **Set up GCP project**:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud auth login
```

2. **Enable APIs**:
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

3. **Deploy backend to Cloud Run**:
```bash
gcloud builds submit --config=cloudbuild.yaml
```

4. **Create Vertex AI Agent**:
   - Go to [Vertex AI Agent Builder](https://console.cloud.google.com/ai/agents)
   - Create new agent
   - Import tools from `agent-tools.json`
   - Use system instructions from `agent-config.yaml`

## Configuration Files

- `agent-config.yaml` - Agent configuration and system instructions
- `agent-tools.json` - Tool definitions for Vertex AI
- `cloudbuild.yaml` - Cloud Build configuration
- `deploy.py` - Python deployment script

## Architecture

```
User → Vertex AI Agent → Cloud Run API → MedAssist Agents
                                    ↓
                              Multi-Agent System
                              (Triage + Medication + Reminder)
```

## Features in Vertex AI

✅ **Conversational Interface**: Natural language interaction
✅ **Tool Integration**: All MedAssist tools available
✅ **Memory Management**: 30-day conversation retention
✅ **Safety Controls**: Medical content safety filters
✅ **Scalability**: Auto-scaling Cloud Run backend
✅ **Monitoring**: Built-in logging and metrics

## Endpoints Available

- **Triage Tool**: Symptom analysis and recommendations
- **Medication Tool**: Drug interaction checking
- **Health Assessment**: Comprehensive parallel analysis

## Cost Optimization

- Cloud Run: Pay-per-request pricing
- Vertex AI: Pay-per-conversation pricing
- Auto-scaling: Scales to zero when not in use

## Monitoring

- **Cloud Run Logs**: Backend API logs
- **Vertex AI Metrics**: Conversation analytics
- **Error Tracking**: Automatic error reporting

## Security

- **IAM Controls**: Role-based access control
- **API Security**: Authenticated endpoints
- **Data Privacy**: HIPAA-compliant infrastructure
- **Safety Filters**: Medical content moderation