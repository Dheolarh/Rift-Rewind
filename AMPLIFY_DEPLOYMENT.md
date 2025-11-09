# Amplify Frontend Deployment Instructions

## Your API Gateway URL
```
https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod
```

## Option 1: Deploy with AWS Amplify (Recommended)

### Step 1: Push to GitHub
```powershell
git add .
git commit -m "Production deployment ready"
git push origin main
```

### Step 2: Connect to Amplify

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **"New app"** → **"Host web app"**
3. Select **GitHub** as your repository provider
4. Authorize AWS Amplify to access your GitHub account
5. Select repository: **`rift-rewind`**
6. Select branch: **`main`**

### Step 3: Configure Build Settings

Amplify should auto-detect the settings. Verify they look like this:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/dist
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

### Step 4: Add Environment Variables

In the Amplify console, go to **"Environment variables"** and add:

| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | `https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod` |

### Step 5: Deploy

1. Click **"Save and deploy"**
2. Wait for build to complete (~3-5 minutes)
3. Amplify will provide you with a URL like: `https://main.xxxxx.amplifyapp.com`

### Step 6: Test Your App

1. Open the Amplify URL
2. Enter a summoner name and test the analysis
3. Check CloudWatch logs if there are issues

---

## Option 2: Manual Build and S3 Hosting

If you prefer to host on S3 + CloudFront:

### 1. Create `.env.production` file

```powershell
cd frontend
New-Item -Name ".env.production" -ItemType File -Force
```

Add this content:
```env
VITE_API_BASE_URL=https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod
```

### 2. Build the frontend

```powershell
npm install
npm run build
```

### 3. Create S3 bucket for hosting

```powershell
$bucketName = "rift-rewind-frontend-$(Get-Random -Maximum 9999)"
aws s3 mb s3://$bucketName --region us-east-1
aws s3 website s3://$bucketName --index-document index.html --error-document index.html
```

### 4. Upload build files

```powershell
aws s3 sync dist/ s3://$bucketName --delete
```

### 5. Make bucket public

Create `policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::BUCKET_NAME/*"
  }]
}
```

Replace `BUCKET_NAME` and apply:
```powershell
aws s3api put-bucket-policy --bucket $bucketName --policy file://policy.json
```

### 6. Get website URL

```powershell
echo "http://$bucketName.s3-website-us-east-1.amazonaws.com"
```

---

## Updating Your Daily Riot API Key

Your Riot API key expires every 24 hours. To update it:

### Update .env file
Edit `backend\.env` and update the `RIOT_API_KEY` value.

### Update Lambda
Run the update script:
```powershell
.\update-lambda-env.ps1
```

This will automatically read from your `.env` file and update Lambda.

Or provide the key directly:
```powershell
.\update-lambda-env.ps1 -RiotApiKey "RGAPI-new-key-here"
```

---

## Testing the API

### Test Lambda directly
```powershell
aws lambda invoke --function-name RiftRewindOrchestrator --payload '{\"playerName\":\"Doublelift\",\"playerTag\":\"NA1\",\"region\":\"na1\"}' --cli-binary-format raw-in-base64-out response.json

Get-Content response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Test API Gateway endpoint
```powershell
$body = @{
    playerName = "Doublelift"
    playerTag = "NA1"
    region = "na1"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod/analyze" -Body $body -ContentType "application/json"
```

---

## Monitoring

### CloudWatch Logs
View logs in AWS Console:
- Lambda logs: `/aws/lambda/RiftRewindOrchestrator`
- Look for:
  - `==> Match Fetching Summary` (duplicate counts)
  - `==> Bedrock raw response` (AI generation)
  - `==> Generated fallback insights` (if AI fails)

### Cost Monitoring
Enable AWS Cost Explorer and set up billing alerts:
- Lambda: ~$0.20 per 1000 analyses
- Bedrock Llama 3.1 70B: ~$2.00 per 1000 analyses
- S3 + API Gateway: ~$0.05 per 1000 analyses

---

## Troubleshooting

### Frontend shows "Failed to fetch"
- Check CORS is enabled in API Gateway
- Verify `VITE_API_BASE_URL` environment variable is set correctly
- Check browser console for actual error message

### Lambda timeout
- Increase timeout: `aws lambda update-function-configuration --function-name RiftRewindOrchestrator --timeout 600`
- Check CloudWatch logs for where it's getting stuck

### Bedrock AccessDenied
- Verify Meta Llama 3.1 70B is enabled in Bedrock console
- Check IAM role has `AmazonBedrockFullAccess` policy
- Wait 2-3 minutes for policy propagation

### "No ranked matches found"
- Player might not have played ranked in 2025
- Check CloudWatch logs for actual API errors
- Verify Riot API key is valid (check expiration)

---

## Production Checklist

- [x] Lambda deployed with correct environment variables
- [x] API Gateway configured with CORS
- [x] S3 bucket created for sessions
- [ ] Frontend deployed to Amplify
- [ ] Test full flow with real summoner
- [ ] Set up CloudWatch alarms for errors
- [ ] Configure S3 lifecycle policy (delete sessions after 30 days)
- [ ] Set up billing alerts
- [ ] Document how to update Riot API key daily

---

## Your Deployment Summary

**Backend (Lambda):**
- Function: `RiftRewindOrchestrator`
- Region: `us-east-1`
- Runtime: `Python 3.11`
- Timeout: `300s` (5 minutes)
- Memory: `1024 MB`
- Model: Meta Llama 3.1 70B Instruct

**API Gateway:**
- API ID: `ueaqinqes3`
- Endpoint: `https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod`
- Stage: `prod`
- CORS: Enabled

**S3 Storage:**
- Bucket: `rift-rewind-sessions-5881`
- Purpose: Session data and analytics storage

**Frontend (Next Step):**
- Deploy to: AWS Amplify
- Environment: `VITE_API_BASE_URL=https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod`

Ready to deploy frontend! 🚀
