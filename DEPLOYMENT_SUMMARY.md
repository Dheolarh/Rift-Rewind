# 🚀 Rift Rewind - Deployment Complete!

## ✅ What's Deployed

### Backend (AWS Lambda)
- **Function Name:** `RiftRewindOrchestrator`
- **Region:** `us-east-1`
- **Runtime:** Python 3.11
- **AI Model:** Meta Llama 3.1 70B Instruct
- **Current API Key:** `RGAPI-4fd0956c-549f-4f63-ad59-a7dc05e4f89d` (expires in 24h)

### API Gateway
- **Endpoint:** `https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod`
- **Resource:** `/analyze` (POST)
- **CORS:** Enabled for all origins

### S3 Storage
- **Bucket:** `rift-rewind-sessions-5881`
- **Purpose:** Session data, analytics, and AI insights storage

---

## 📋 Next Steps

### 1. Deploy Frontend to AWS Amplify

#### Quick Start:
1. **Push to GitHub:**
   ```powershell
   git add .
   git commit -m "Production deployment ready"
   git push origin main
   ```

2. **Go to AWS Amplify Console:**
   - https://console.aws.amazon.com/amplify/

3. **Create New App:**
   - Click "New app" → "Host web app"
   - Connect to GitHub
   - Select repository: `Dheolarh/rift-rewind`
   - Select branch: `main`

4. **Add Environment Variable:**
   - In Amplify settings, add:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod`

5. **Deploy:**
   - Click "Save and deploy"
   - Wait 3-5 minutes for build
   - Get your live URL: `https://main.xxxxx.amplifyapp.com`

### 2. Daily API Key Update

Your Riot API key expires every 24 hours. To update:

#### Option A: Automatic (from .env file)
1. Update `backend\.env` with new API key
2. Run:
   ```powershell
   .\update-lambda-env.ps1
   ```

#### Option B: Manual
```powershell
.\update-lambda-env.ps1 -RiotApiKey "RGAPI-new-key-here"
```

---

## 🧪 Testing

### Test API Gateway
```powershell
$body = @{
    playerName = "Doublelift"
    playerTag = "NA1"
    region = "na1"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod/analyze" -Body $body -ContentType "application/json"
```

### Test Lambda Directly
```powershell
aws lambda invoke --function-name RiftRewindOrchestrator --payload '{\"playerName\":\"Doublelift\",\"playerTag\":\"NA1\",\"region\":\"na1\"}' --cli-binary-format raw-in-base64-out response.json

Get-Content response.json
```

---

## 📊 Monitoring

### CloudWatch Logs
View Lambda logs at:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252FRiftRewindOrchestrator
```

**Look for these log messages:**
- `==> Match Fetching Summary` - Shows duplicate counts by queue
- `==> Bedrock raw response` - AI generation details
- `==> Parsed JSON successfully` - AI insights validation
- `==> Generated fallback insights` - If AI fails

### Key Metrics to Watch
- Lambda invocations
- Lambda errors
- API Gateway 4xx/5xx errors
- Bedrock API calls
- S3 storage size

---

## 💰 Cost Estimate

**For 1,000 player analyses:**
- Lambda: $0.20
- Bedrock (Llama 3.1 70B): $2.00
- S3: $0.02
- API Gateway: $0.01
- **Total: ~$2.23 per 1,000 analyses**

Set up billing alerts:
```powershell
# Create billing alarm for $10/month
aws cloudwatch put-metric-alarm --alarm-name rift-rewind-billing --alarm-description "Alert when Rift Rewind costs exceed $10" --metric-name EstimatedCharges --namespace AWS/Billing --statistic Maximum --period 21600 --threshold 10 --comparison-operator GreaterThanThreshold
```

---

## 🔧 Troubleshooting

### Issue: "AccessDeniedException" from Bedrock
**Fix:** Verify Meta Llama 3.1 70B is enabled
1. Go to Bedrock console: https://console.aws.amazon.com/bedrock/
2. Click "Model access" in left sidebar
3. Find "Meta Llama 3.1 70B Instruct"
4. Click "Modify model access" and enable it

### Issue: Frontend can't connect to API
**Fix:** Check CORS and environment variable
1. Verify `VITE_API_BASE_URL` is set in Amplify
2. Test API directly with curl/PowerShell
3. Check browser console for CORS errors

### Issue: Lambda timeout
**Fix:** Increase timeout to 10 minutes
```powershell
aws lambda update-function-configuration --function-name RiftRewindOrchestrator --timeout 600
```

### Issue: "No ranked matches found"
**Causes:**
- Player hasn't played ranked in 2025
- Riot API key expired
- Region mismatch

**Fix:**
1. Check CloudWatch logs for actual error
2. Verify API key: `aws lambda get-function-configuration --function-name RiftRewindOrchestrator --query Environment.Variables.RIOT_API_KEY`
3. Update if expired: `.\update-lambda-env.ps1`

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `deploy-simple.ps1` | Deploy/update Lambda function |
| `setup-api-gateway.ps1` | Create API Gateway |
| `update-lambda-env.ps1` | Update Riot API key daily |
| `backend\.env` | Local development config |
| `frontend\.env.production` | Production API endpoint |
| `AMPLIFY_DEPLOYMENT.md` | Detailed Amplify instructions |

---

## 🎉 Success Criteria

- [x] Lambda deployed with Meta Llama 3.1 70B
- [x] API Gateway created with CORS
- [x] S3 bucket for session storage
- [x] Environment variables configured
- [x] Update scripts created for daily API key rotation
- [ ] Frontend deployed to Amplify
- [ ] End-to-end test with real player
- [ ] Monitoring and alerts set up

---

## 📞 Quick Commands Reference

```powershell
# Update Riot API key
.\update-lambda-env.ps1

# Redeploy Lambda with code changes
.\deploy-simple.ps1 -RiotApiKey "RGAPI-xxxxx"

# View Lambda logs
aws logs tail /aws/lambda/RiftRewindOrchestrator --follow

# Test API
Invoke-RestMethod -Method Post -Uri "https://ueaqinqes3.execute-api.us-east-1.amazonaws.com/prod/analyze" -Body '{"playerName":"Doublelift","playerTag":"NA1","region":"na1"}' -ContentType "application/json"

# Check Lambda config
aws lambda get-function-configuration --function-name RiftRewindOrchestrator

# Update timeout
aws lambda update-function-configuration --function-name RiftRewindOrchestrator --timeout 600

# Update memory
aws lambda update-function-configuration --function-name RiftRewindOrchestrator --memory-size 2048
```

---

**Your deployment is ready! 🚀**

Next: Deploy frontend to Amplify following [AMPLIFY_DEPLOYMENT.md](./AMPLIFY_DEPLOYMENT.md)
