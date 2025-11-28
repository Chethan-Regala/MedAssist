#!/usr/bin/env python3
"""Deploy MedAssist to Vertex AI Agent Engine."""

import json
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and return result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def deploy_to_vertex_ai():
    """Deploy MedAssist agent to Vertex AI."""
    
    print("🚀 Deploying MedAssist to Vertex AI Agent Engine...")
    
    # Check if gcloud is installed
    result = run_command("gcloud --version", check=False)
    if result.returncode != 0:
        print("❌ Google Cloud SDK not found. Please install gcloud CLI first.")
        print("   Download from: https://cloud.google.com/sdk/docs/install")
        return False
    
    # Get project ID
    result = run_command("gcloud config get-value project", check=False)
    if not result.stdout.strip():
        print("❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID")
        return False
    
    project_id = result.stdout.strip()
    print(f"📋 Using project: {project_id}")
    
    # Enable required APIs
    print("🔧 Enabling required APIs...")
    apis = [
        "aiplatform.googleapis.com",
        "cloudbuild.googleapis.com",
        "run.googleapis.com"
    ]
    
    for api in apis:
        run_command(f"gcloud services enable {api}")
    
    # Deploy to Cloud Run first (for API backend)
    print("☁️ Deploying API backend to Cloud Run...")
    
    # Build and deploy
    run_command("gcloud builds submit --tag gcr.io/{}/medassist".format(project_id))
    
    run_command(f"""gcloud run deploy medassist-api \\
        --image gcr.io/{project_id}/medassist \\
        --platform managed \\
        --region us-central1 \\
        --allow-unauthenticated \\
        --port 8000 \\
        --memory 2Gi \\
        --cpu 1 \\
        --max-instances 10 \\
        --set-env-vars LOG_LEVEL=INFO""")
    
    # Get Cloud Run URL
    result = run_command(f"gcloud run services describe medassist-api --region us-central1 --format 'value(status.url)'")
    api_url = result.stdout.strip()
    print(f"📡 API deployed at: {api_url}")
    
    # Create Vertex AI Agent
    print("🤖 Creating Vertex AI Agent...")
    
    agent_config = {
        "displayName": "MedAssist Healthcare AI",
        "description": "Multi-agent healthcare assistant with triage, medication safety, and monitoring",
        "defaultLanguageCode": "en",
        "timeZone": "UTC",
        "startFlow": "projects/{}/locations/us-central1/agents/{}/flows/00000000-0000-0000-0000-000000000000".format(project_id, "medassist-agent"),
        "supportedLanguageCodes": ["en"],
        "textToSpeechSettings": {
            "enableTextToSpeech": True
        }
    }
    
    # Write agent config
    with open("agent-temp.json", "w") as f:
        json.dump(agent_config, f, indent=2)
    
    # Create agent
    run_command(f"""gcloud alpha dialogflow agents create \\
        --display-name="MedAssist Healthcare AI" \\
        --description="Multi-agent healthcare assistant" \\
        --default-language-code=en \\
        --time-zone=UTC \\
        --location=us-central1""")
    
    print("✅ Vertex AI Agent deployment complete!")
    print(f"🌐 API Backend: {api_url}")
    print(f"🤖 Agent Console: https://console.cloud.google.com/ai/agents")
    
    return True

if __name__ == "__main__":
    success = deploy_to_vertex_ai()
    if success:
        print("\n🎉 MedAssist successfully deployed to Vertex AI!")
    else:
        print("\n❌ Deployment failed. Check the logs above.")
        sys.exit(1)