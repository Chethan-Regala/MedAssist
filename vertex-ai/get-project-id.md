# How to Get Your Google Cloud Project ID

## Method 1: Create New Project (Recommended)

1. **Go to Google Cloud Console**: https://console.cloud.google.com
2. **Sign in** with your Google account
3. **Click the project dropdown** (top left, next to "Google Cloud")
4. **Click "NEW PROJECT"**
5. **Enter project details**:
   - Project name: `medassist-deployment` (or any name you prefer)
   - Organization: Leave default
   - Location: Leave default
6. **Click "CREATE"**
7. **Copy the Project ID** (it will be auto-generated, like `medassist-deployment-123456`)

## Method 2: Use Existing Project

1. **Go to**: https://console.cloud.google.com
2. **Click the project dropdown** (top left)
3. **Select your existing project**
4. **Copy the Project ID** from the dropdown or dashboard

## Method 3: List Projects via Command Line (if gcloud installed)

```bash
gcloud projects list
```

## Method 4: From Google Cloud Console Dashboard

1. **Go to**: https://console.cloud.google.com/home/dashboard
2. **Look for "Project Info" card**
3. **Copy the Project ID** shown there

## What Your Project ID Looks Like

- Format: `project-name-123456` or `my-project-id`
- Examples: 
  - `medassist-deployment-789123`
  - `healthcare-ai-project`
  - `my-vertex-ai-demo`

## Important Notes

- **Project ID is unique globally** across all Google Cloud
- **Cannot be changed** after creation
- **Use lowercase letters, numbers, and hyphens only**
- **Must be 6-30 characters long**

## For MedAssist Deployment

**Recommended Project ID format**: `medassist-[your-name]-[random-numbers]`

Example: `medassist-john-456789`

## Next Steps

Once you have your Project ID:

1. **Replace `YOUR_PROJECT_ID`** in all commands with your actual Project ID
2. **Enable billing** for the project (required for Cloud Run)
3. **Continue with the deployment steps**

## Enable Billing

1. Go to: https://console.cloud.google.com/billing
2. Select your project
3. Link a billing account (free tier available)
4. This is required for Cloud Run deployment