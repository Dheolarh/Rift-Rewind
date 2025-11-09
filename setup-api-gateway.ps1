# Create and configure API Gateway for Rift Rewind
param(
    [string]$Region = "us-east-1",
    [string]$ApiName = "RiftRewindAPI"
)

Write-Host "`nCREATING API GATEWAY`n" -ForegroundColor Cyan

# Get Lambda function ARN
Write-Host "[1/6] Getting Lambda function ARN..." -ForegroundColor Yellow
$lambdaArn = aws lambda get-function --function-name RiftRewindOrchestrator --region $Region --query 'Configuration.FunctionArn' --output text
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Lambda function not found. Deploy Lambda first!" -ForegroundColor Red
    exit 1
}
Write-Host "OK Lambda ARN: $lambdaArn" -ForegroundColor Green

# Get AWS Account ID
$accountId = aws sts get-caller-identity --query 'Account' --output text

# Create REST API
Write-Host "[2/6] Creating REST API..." -ForegroundColor Yellow
$apiId = aws apigateway create-rest-api --name $ApiName --description "Rift Rewind API" --region $Region --query 'id' --output text 2>$null

if (-not $apiId) {
    # API might already exist, try to get it
    $apiId = aws apigateway get-rest-apis --region $Region --query "items[?name=='$ApiName'].id" --output text
    if ($apiId) {
        Write-Host "OK API already exists: $apiId" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create/find API" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "OK API created: $apiId" -ForegroundColor Green
}

# Get root resource ID
$rootId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query 'items[?path==`/`].id' --output text

# Create /analyze resource
Write-Host "[3/6] Creating /analyze resource..." -ForegroundColor Yellow
$analyzeId = aws apigateway create-resource --rest-api-id $apiId --parent-id $rootId --path-part analyze --region $Region --query 'id' --output text 2>$null

if (-not $analyzeId) {
    # Resource might already exist
    $analyzeId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query "items[?path=='/analyze'].id" --output text
    Write-Host "OK Resource already exists: $analyzeId" -ForegroundColor Green
} else {
    Write-Host "OK Resource created: $analyzeId" -ForegroundColor Green
}

# Create POST method
Write-Host "[4/6] Creating POST method..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $analyzeId --http-method POST --authorization-type NONE --region $Region 2>$null | Out-Null

# Set Lambda integration
$lambdaUri = "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/$lambdaArn/invocations"
aws apigateway put-integration --rest-api-id $apiId --resource-id $analyzeId --http-method POST --type AWS_PROXY --integration-http-method POST --uri $lambdaUri --region $Region 2>$null | Out-Null
Write-Host "OK POST method configured" -ForegroundColor Green

# Add Lambda permission
Write-Host "[5/6] Adding Lambda permissions..." -ForegroundColor Yellow
$sourceArn = "arn:aws:execute-api:${Region}:${accountId}:${apiId}/*/*/analyze"
aws lambda add-permission --function-name RiftRewindOrchestrator --statement-id apigateway-access-$(Get-Random) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArn --region $Region 2>$null | Out-Null
Write-Host "OK Lambda permissions added" -ForegroundColor Green

# Enable CORS
Write-Host "[6/6] Enabling CORS..." -ForegroundColor Yellow

# Add OPTIONS method for CORS preflight
aws apigateway put-method --rest-api-id $apiId --resource-id $analyzeId --http-method OPTIONS --authorization-type NONE --region $Region 2>$null | Out-Null

# Mock integration for OPTIONS
aws apigateway put-integration --rest-api-id $apiId --resource-id $analyzeId --http-method OPTIONS --type MOCK --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $Region 2>$null | Out-Null

# OPTIONS method response
aws apigateway put-method-response --rest-api-id $apiId --resource-id $analyzeId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null

# OPTIONS integration response
$corsHeaders = @{
    'method.response.header.Access-Control-Allow-Headers' = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    'method.response.header.Access-Control-Allow-Methods' = "'POST,OPTIONS'"
    'method.response.header.Access-Control-Allow-Origin' = "'*'"
}
$corsHeadersJson = $corsHeaders | ConvertTo-Json -Compress
aws apigateway put-integration-response --rest-api-id $apiId --resource-id $analyzeId --http-method OPTIONS --status-code 200 --response-parameters $corsHeadersJson --region $Region 2>$null | Out-Null

# Add CORS headers to POST responses
aws apigateway put-method-response --rest-api-id $apiId --resource-id $analyzeId --http-method POST --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null

Write-Host "OK CORS enabled" -ForegroundColor Green

# Deploy API
Write-Host "`nDeploying API to 'prod' stage..." -ForegroundColor Yellow
aws apigateway create-deployment --rest-api-id $apiId --stage-name prod --region $Region 2>$null | Out-Null
Write-Host "OK API deployed" -ForegroundColor Green

# Output API URL
$apiUrl = "https://${apiId}.execute-api.${Region}.amazonaws.com/prod"
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "API GATEWAY CREATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nAPI Endpoint:" -ForegroundColor White
Write-Host "  $apiUrl" -ForegroundColor Yellow
Write-Host "`nTest with:" -ForegroundColor White
Write-Host "  curl -X POST $apiUrl/analyze \`" -ForegroundColor Gray
Write-Host "    -H 'Content-Type: application/json' \`" -ForegroundColor Gray
Write-Host "    -d '{\"playerName\":\"Doublelift\",\"playerTag\":\"NA1\",\"region\":\"na1\"}'" -ForegroundColor Gray
Write-Host "`nFor Amplify Frontend:" -ForegroundColor White
Write-Host "  Set environment variable: VITE_API_BASE_URL=$apiUrl" -ForegroundColor Yellow
Write-Host ""
