# Quick script to update Lambda environment variables
# Use this to update your Riot API key daily

param(
    [string]$RiotApiKey,
    [string]$BucketName = "rift-rewind-sessions",
    [string]$Region = "us-east-1",
    [string]$BedrockModelId = "us.meta.llama3-1-70b-instruct-v1:0"
)

Write-Host "`nUPDATING LAMBDA ENVIRONMENT VARIABLES`n" -ForegroundColor Cyan

# If no API key provided, try to read from .env file
if (-not $RiotApiKey) {
    if (Test-Path "backend\.env") {
        Write-Host "Reading API key from backend\.env..." -ForegroundColor Yellow
        $envContent = Get-Content "backend\.env"
        $keyLine = $envContent | Where-Object { $_ -match "^RIOT_API_KEY=" }
        if ($keyLine) {
            $RiotApiKey = $keyLine -replace "^RIOT_API_KEY=", ""
            Write-Host "OK Found API key in .env" -ForegroundColor Green
        }
    }
}

if (-not $RiotApiKey) {
    Write-Host "ERROR: No Riot API key provided and not found in .env" -ForegroundColor Red
    Write-Host "Usage: .\update-lambda-env.ps1 -RiotApiKey 'RGAPI-xxxxx'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Updating Lambda function: RiftRewindOrchestrator..." -ForegroundColor Yellow
aws lambda update-function-configuration `
    --function-name RiftRewindOrchestrator `
    --region $Region `
    --environment "Variables={RIOT_API_KEY=$RiotApiKey,S3_BUCKET_NAME=$BucketName,BEDROCK_MODEL_ID=$BedrockModelId}" | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Lambda environment updated successfully" -ForegroundColor Green
    Write-Host "`nCurrent configuration:" -ForegroundColor White
    Write-Host "  API Key: $($RiotApiKey.Substring(0,15))..." -ForegroundColor Gray
    Write-Host "  S3 Bucket: $BucketName" -ForegroundColor Gray
    Write-Host "  Region: $Region" -ForegroundColor Gray
    Write-Host "  Bedrock Model: $BedrockModelId" -ForegroundColor Gray
} else {
    Write-Host "ERROR: Failed to update Lambda environment" -ForegroundColor Red
    exit 1
}

Write-Host "`nTIP: Add this to your daily routine to update the API key!" -ForegroundColor Yellow
Write-Host "  .\update-lambda-env.ps1`n" -ForegroundColor Gray
