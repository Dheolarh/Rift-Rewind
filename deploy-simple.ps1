param(
    [Parameter(Mandatory=$true)]
    [string]$RiotApiKey,
    [string]$BucketName = "rift-rewind-sessions-$(Get-Random -Maximum 9999)",
    [string]$Region = "us-east-1"
)

Write-Host "`nRIFT REWIND - AWS DEPLOYMENT`n" -ForegroundColor Cyan

# 1. Check AWS CLI
Write-Host "[1/8] Checking AWS CLI..." -ForegroundColor Yellow
try {
    aws --version | Out-Null
    Write-Host "OK AWS CLI found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: AWS CLI not installed" -ForegroundColor Red
    exit 1
}

# 2. Check credentials
Write-Host "[2/8] Checking AWS credentials..." -ForegroundColor Yellow
$accountId = aws sts get-caller-identity --query 'Account' --output text
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Account: $accountId" -ForegroundColor Green
} else {
    Write-Host "ERROR: AWS credentials not configured" -ForegroundColor Red
    exit 1
}

# 3. Create S3 bucket
Write-Host "[3/8] Creating S3 bucket: $BucketName..." -ForegroundColor Yellow
aws s3 mb "s3://$BucketName" --region $Region 2>$null
if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 255) {
    Write-Host "OK S3 bucket ready" -ForegroundColor Green
}

# 4. Create IAM role
Write-Host "[4/8] Creating IAM role..." -ForegroundColor Yellow
$trustPolicyJson = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
$trustPolicyJson | Out-File -FilePath "trust.json" -Encoding ASCII
aws iam create-role --role-name RiftRewindLambdaRole --assume-role-policy-document file://trust.json 2>$null
Remove-Item "trust.json"

aws iam attach-role-policy --role-name RiftRewindLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>$null
aws iam attach-role-policy --role-name RiftRewindLambdaRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess 2>$null
aws iam attach-role-policy --role-name RiftRewindLambdaRole --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess 2>$null
Write-Host "OK IAM role configured" -ForegroundColor Green

# 5. Wait for IAM
Write-Host "[5/8] Waiting for IAM propagation..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "OK Ready" -ForegroundColor Green

# 6. Create Lambda package
Write-Host "[6/8] Creating Lambda package..." -ForegroundColor Yellow
Push-Location backend
if (Test-Path "lambda-package") { Remove-Item -Recurse -Force "lambda-package" }
New-Item -ItemType Directory -Path "lambda-package" | Out-Null

# Copy Lambda function files (Python files only, not subdirectories)
Get-ChildItem "lambdas\*.py" | Copy-Item -Destination "lambda-package\"

# Copy services directory
Copy-Item -Recurse "services" "lambda-package\"

# Install dependencies
Push-Location lambda-package
pip install -r ..\requirements.txt -t . --quiet 2>$null
Compress-Archive -Path * -DestinationPath ..\rift-rewind-lambda.zip -Force
Pop-Location
Remove-Item -Recurse -Force "lambda-package"
Pop-Location
Write-Host "OK Lambda package created" -ForegroundColor Green

# 7. Deploy Lambda
Write-Host "[7/8] Deploying Lambda function..." -ForegroundColor Yellow
$roleArn = aws iam get-role --role-name RiftRewindLambdaRole --query 'Role.Arn' --output text

# Check if function exists
$functionExists = aws lambda get-function --function-name RiftRewindOrchestrator --region $Region 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Updating existing function..." -ForegroundColor Yellow
    aws lambda update-function-code --function-name RiftRewindOrchestrator --zip-file fileb://backend/rift-rewind-lambda.zip --region $Region | Out-Null
    Start-Sleep -Seconds 2
    aws lambda update-function-configuration --function-name RiftRewindOrchestrator --environment Variables="{RIOT_API_KEY=$RiotApiKey,S3_BUCKET_NAME=$BucketName,BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0}" --region $Region | Out-Null
    Write-Host "OK Lambda function updated" -ForegroundColor Green
} else {
    Write-Host "Creating new function..." -ForegroundColor Yellow
    aws lambda create-function --function-name RiftRewindOrchestrator --runtime python3.11 --role $roleArn --handler orchestrator.lambda_handler --zip-file fileb://backend/rift-rewind-lambda.zip --timeout 300 --memory-size 1024 --region $Region --environment Variables="{RIOT_API_KEY=$RiotApiKey,S3_BUCKET_NAME=$BucketName,BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0}" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Lambda function created" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create Lambda function. Wait 30s and try again." -ForegroundColor Red
    }
}

# 8. Summary
Write-Host "`n[8/8] DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "Bucket: $BucketName" -ForegroundColor White
Write-Host "Lambda: RiftRewindOrchestrator" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host "`nNext: Enable Bedrock access in AWS Console`n" -ForegroundColor Yellow
