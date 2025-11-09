# Rift Rewind - AWS Deployment Guide

## Prerequisites Checklist

### 1. AWS Account Setup
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS credentials configured (`aws configure`)
- [ ] IAM permissions for: Lambda, S3, IAM, Bedrock

### 2. Bedrock Model Access
- [ ] Navigate to AWS Bedrock console
- [ ] Go to "Model access" in the left sidebar
- [ ] Request access to: **Meta Llama 3.1 70B Instruct** (`us.meta.llama3-1-70b-instruct-v1:0`)
- [ ] Wait for access approval (usually instant for Llama models)

### 3. Riot API Key
- [ ] Get your Riot API key from: https://developer.riotgames.com/
- [ ] Copy the API key (you'll need it for deployment)

## Deployment Steps

### Step 1: Deploy Backend (Lambda + S3)

Run the deployment script with your Riot API key:

```powershell
.\deploy-simple.ps1 -RiotApiKey "RGAPI-your-key-here"
```

**Optional parameters:**
- `-BucketName` - Custom S3 bucket name (default: auto-generated)
- `-Region` - AWS region (default: us-east-1)

Example with custom settings:
```powershell
.\deploy-simple.ps1 -RiotApiKey "RGAPI-xxxxx" -Region "us-west-2" -BucketName "my-rift-rewind-bucket"
```

**What this creates:**
- ✅ S3 bucket for session storage
- ✅ IAM role with Lambda, S3, and Bedrock permissions
- ✅ Lambda function: `RiftRewindOrchestrator`
- ✅ Environment variables configured (RIOT_API_KEY, S3_BUCKET_NAME, BEDROCK_MODEL_ID)

### Step 2: Update Bedrock Model ID (Important!)

The deploy script sets Claude by default, but our code uses Llama. Update it:

```powershell
aws lambda update-function-configuration `
  --function-name RiftRewindOrchestrator `
  --environment Variables="{RIOT_API_KEY=your-key,S3_BUCKET_NAME=your-bucket,BEDROCK_MODEL_ID=us.meta.llama3-1-70b-instruct-v1:0}"
```

Replace `your-key` and `your-bucket` with your actual values.

### Step 3: Create API Gateway

1. Go to AWS API Gateway console
2. Create new **REST API**
3. Create resource: `/analyze`
4. Create method: `POST`
5. Integration type: Lambda Function
6. Select: `RiftRewindOrchestrator`
7. Enable CORS
8. Deploy to stage: `prod`
9. Copy the **Invoke URL** (e.g., `https://xyz123.execute-api.us-east-1.amazonaws.com/prod`)

### Step 4: Deploy Frontend (AWS Amplify)

1. Go to AWS Amplify console
2. Click "New app" → "Host web app"
3. Connect your GitHub repository
4. Build settings (auto-detected):
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend
           - npm install
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
5. Environment variables:
   - `VITE_API_BASE_URL` = Your API Gateway URL (e.g., `https://xyz123.execute-api.us-east-1.amazonaws.com/prod`)
6. Save and deploy

### Step 5: Update Frontend API Configuration (Local Build)

If deploying manually without Amplify:

1. Update `frontend/src/services/api.ts`:
   ```typescript
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://your-api-gateway-url.com/prod';
   ```

2. Build frontend:
   ```powershell
   cd frontend
   npm install
   npm run build
   ```

3. Upload `frontend/dist` to S3 or hosting service

## Testing Deployment

### Test Lambda Function

```powershell
aws lambda invoke `
  --function-name RiftRewindOrchestrator `
  --payload '{\"playerName\":\"Doublelift\",\"playerTag\":\"NA1\",\"region\":\"na1\"}' `
  --cli-binary-format raw-in-base64-out `
  response.json

cat response.json
```

### Test API Gateway

```powershell
curl -X POST https://your-api-gateway-url/prod/analyze `
  -H "Content-Type: application/json" `
  -d '{\"playerName\":\"Doublelift\",\"playerTag\":\"NA1\",\"region\":\"na1\"}'
```

## Troubleshooting

### Bedrock Access Denied
**Error:** `AccessDeniedException` when calling Bedrock
**Fix:** 
1. Go to Bedrock console → Model access
2. Enable "Meta Llama 3.1 70B Instruct"
3. Wait 2-3 minutes for propagation

### Lambda Timeout
**Error:** Task timed out after 300 seconds
**Fix:** Increase timeout (if needed):
```powershell
aws lambda update-function-configuration --function-name RiftRewindOrchestrator --timeout 600
```

### S3 Access Denied
**Error:** Cannot write to S3 bucket
**Fix:** Check IAM role has `AmazonS3FullAccess` policy attached

### CORS Issues
**Error:** Frontend can't connect to API
**Fix:** 
1. Enable CORS in API Gateway
2. Add `OPTIONS` method to `/analyze` resource
3. Redeploy API

## Environment Variables Reference

### Lambda Environment Variables
- `RIOT_API_KEY` - Your Riot Games API key
- `S3_BUCKET_NAME` - S3 bucket for session storage
- `BEDROCK_MODEL_ID` - AI model ID (`us.meta.llama3-1-70b-instruct-v1:0`)
- `AWS_DEFAULT_REGION` - AWS region (auto-set by Lambda)

### Frontend Environment Variables
- `VITE_API_BASE_URL` - API Gateway invoke URL

## Cost Estimation

**Typical costs for 1000 analyses:**
- Lambda: ~$0.20 (300s avg × $0.0000166667/GB-second)
- S3: ~$0.02 (storage + requests)
- Bedrock Llama 3.1 70B: ~$2.00 (1M input tokens, 100K output tokens)
- API Gateway: ~$0.01 (1000 requests)
- **Total: ~$2.23 per 1000 analyses**

## Production Checklist

- [ ] Lambda timeout set appropriately (300-600s)
- [ ] Lambda memory optimized (1024MB minimum)
- [ ] API Gateway throttling configured
- [ ] CloudWatch logs retention set (7-30 days)
- [ ] S3 lifecycle policy for old sessions (auto-delete after 30 days)
- [ ] Frontend CDN configured (Amplify handles this)
- [ ] Error monitoring set up (CloudWatch Alarms)
- [ ] Bedrock model access confirmed

## Cleanup

To remove all AWS resources:

```powershell
.\cleanup-aws.ps1 -BucketName "your-bucket-name"
```

This will delete:
- Lambda function
- S3 bucket and all objects
- IAM role and policies
