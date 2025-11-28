#!/bin/bash

# MedAssist Cloud Deployment Script
# Supports Google Cloud Run, AWS ECS, and Azure Container Instances

PLATFORM=${1:-"gcp"}
PROJECT_ID=${2:-"your-project-id"}
REGION=${3:-"us-central1"}

echo "Deploying MedAssist to $PLATFORM..."

case $PLATFORM in
    "gcp"|"google")
        echo "Deploying to Google Cloud Run..."
        
        # Build and push to Google Container Registry
        gcloud builds submit --tag gcr.io/$PROJECT_ID/medassist
        
        # Deploy to Cloud Run
        gcloud run deploy medassist \
            --image gcr.io/$PROJECT_ID/medassist \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated \
            --port 8000 \
            --memory 1Gi \
            --cpu 1 \
            --set-env-vars "LOG_LEVEL=INFO" \
            --max-instances 10
        
        echo "Deployment complete!"
        echo "URL: https://medassist-$(gcloud config get-value project).a.run.app"
        ;;
        
    "aws")
        echo "Deploying to AWS ECS..."
        
        # Build and push to ECR
        aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
        docker build -t medassist .
        docker tag medassist:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/medassist:latest
        docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/medassist:latest
        
        echo "Please configure ECS service manually or use AWS CDK/CloudFormation"
        ;;
        
    "azure")
        echo "Deploying to Azure Container Instances..."
        
        # Build and push to Azure Container Registry
        az acr build --registry $ACR_NAME --image medassist .
        
        # Deploy to Container Instances
        az container create \
            --resource-group $RESOURCE_GROUP \
            --name medassist \
            --image $ACR_NAME.azurecr.io/medassist:latest \
            --cpu 1 \
            --memory 1 \
            --ports 8000 \
            --environment-variables LOG_LEVEL=INFO
        
        echo "Deployment complete!"
        ;;
        
    *)
        echo "Unsupported platform: $PLATFORM"
        echo "Supported platforms: gcp, aws, azure"
        exit 1
        ;;
esac