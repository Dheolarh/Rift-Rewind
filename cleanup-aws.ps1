# Rift Rewind - AWS Cleanup Script
# WARNING: This will delete ALL Rift Rewind resources from AWS

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

if (-not $Force) {
    Write-Host "`n⚠️  WARNING: This will DELETE all Rift Rewind resources from AWS!" -ForegroundColor Red
    Write-Host "This includes:" -ForegroundColor Yellow
    Write-Host "  - S3 bucket and all data" -ForegroundColor Yellow
    Write-Host "  - Lambda functions" -ForegroundColor Yellow
    Write-Host "  - API Gateway" -ForegroundColor Yellow
    Write-Host "  - IAM roles" -ForegroundColor Yellow
    
    $confirm = Read-Host "`nType 'DELETE' to confirm"
    if ($confirm -ne "DELETE") {
        Write-Host "`nCleanup cancelled." -ForegroundColor Green
        exit 0
    }
}

Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  RIFT REWIND - AWS CLEANUP                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Load configuration
if (Test-Path "deployment-config.json") {
    $config = Get-Content "deployment-config.json" | ConvertFrom-Json
    $bucketName = $config.BucketName
    $region = $config.Region
} else {
    Write-Host "⚠️  No deployment-config.json found. Using defaults..." -ForegroundColor Yellow
    $bucketName = Read-Host "Enter S3 bucket name to delete"
    $region = "us-east-1"
}

# Delete Lambda functions
Write-Host "[1/5] Deleting Lambda functions..." -ForegroundColor Yellow
try {
    aws lambda delete-function --function-name RiftRewindOrchestrator --region $region 2>&1 | Out-Null
    Write-Host "✓ Lambda function deleted" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Lambda function not found or already deleted" -ForegroundColor Yellow
}

# Delete API Gateway
Write-Host "`n[2/5] Deleting API Gateway..." -ForegroundColor Yellow
try {
    $apis = aws apigateway get-rest-apis --region $region --query 'items[?name==`RiftRewindAPI`].id' --output text
    foreach ($apiId in $apis -split '\s+') {
        if ($apiId) {
            aws apigateway delete-rest-api --rest-api-id $apiId --region $region
            Write-Host "✓ API Gateway deleted: $apiId" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "⚠️  API Gateway not found or already deleted" -ForegroundColor Yellow
}

# Delete S3 bucket
Write-Host "`n[3/5] Deleting S3 bucket..." -ForegroundColor Yellow
try {
    aws s3 rm "s3://$bucketName" --recursive 2>&1 | Out-Null
    aws s3 rb "s3://$bucketName" --force
    Write-Host "✓ S3 bucket deleted: $bucketName" -ForegroundColor Green
} catch {
    Write-Host "⚠️  S3 bucket not found or already deleted" -ForegroundColor Yellow
}

# Delete IAM role
Write-Host "`n[4/5] Deleting IAM role..." -ForegroundColor Yellow
try {
    aws iam detach-role-policy --role-name RiftRewindLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>&1 | Out-Null
    aws iam detach-role-policy --role-name RiftRewindLambdaRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess 2>&1 | Out-Null
    aws iam detach-role-policy --role-name RiftRewindLambdaRole --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess 2>&1 | Out-Null
    aws iam delete-role --role-name RiftRewindLambdaRole
    Write-Host "✓ IAM role deleted" -ForegroundColor Green
} catch {
    Write-Host "⚠️  IAM role not found or already deleted" -ForegroundColor Yellow
}

# Clean up local files
Write-Host "`n[5/5] Cleaning up local files..." -ForegroundColor Yellow
if (Test-Path "backend\lambda-package") {
    Remove-Item -Recurse -Force "backend\lambda-package"
}
if (Test-Path "backend\rift-rewind-lambda.zip") {
    Remove-Item -Force "backend\rift-rewind-lambda.zip"
}
if (Test-Path "deployment-config.json") {
    Remove-Item -Force "deployment-config.json"
}
Write-Host "✓ Local files cleaned up" -ForegroundColor Green

Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CLEANUP COMPLETE                                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "All Rift Rewind resources have been removed from AWS.`n" -ForegroundColor Green
