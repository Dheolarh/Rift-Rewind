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

# Enable CORS for /analyze
Write-Host "[6/6] Enabling CORS for /analyze..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $analyzeId --http-method OPTIONS --authorization-type NONE --region $Region 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $analyzeId --http-method OPTIONS --type MOCK --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $analyzeId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
$corsHeaders = @{
    'method.response.header.Access-Control-Allow-Headers' = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    'method.response.header.Access-Control-Allow-Methods' = "'POST,OPTIONS'"
    'method.response.header.Access-Control-Allow-Origin' = "'*'"
}
$corsHeadersJson = $corsHeaders | ConvertTo-Json -Compress
aws apigateway put-integration-response --rest-api-id $apiId --resource-id $analyzeId --http-method OPTIONS --status-code 200 --response-parameters $corsHeadersJson --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $analyzeId --http-method POST --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
Write-Host "OK CORS enabled for /analyze" -ForegroundColor Green

# --- Create /api resource ---
Write-Host "[3b/6] Creating /api resource..." -ForegroundColor Yellow
$apiResourceId = aws apigateway create-resource --rest-api-id $apiId --parent-id $rootId --path-part api --region $Region --query 'id' --output text 2>$null
if (-not $apiResourceId) {
    $apiResourceId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query "items[?path=='/api'].id" --output text
    Write-Host "OK Resource already exists: $apiResourceId" -ForegroundColor Green
} else {
    Write-Host "OK Resource created: $apiResourceId" -ForegroundColor Green
}

# --- Create /api/regions resource ---
Write-Host "[3c/6] Creating /api/regions resource..." -ForegroundColor Yellow
$regionsId = aws apigateway create-resource --rest-api-id $apiId --parent-id $apiResourceId --path-part regions --region $Region --query 'id' --output text 2>$null
if (-not $regionsId) {
    $regionsId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query "items[?path=='/api/regions'].id" --output text
    Write-Host "OK Resource already exists: $regionsId" -ForegroundColor Green
} else {
    Write-Host "OK Resource created: $regionsId" -ForegroundColor Green
}

# --- Add GET method to /api/regions ---
Write-Host "[4b/6] Creating GET method for /api/regions..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $regionsId --http-method GET --authorization-type NONE --region $Region 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $regionsId --http-method GET --type AWS_PROXY --integration-http-method POST --uri $lambdaUri --region $Region 2>$null | Out-Null
Write-Host "OK GET method configured" -ForegroundColor Green

# --- Add Lambda permission for /api/regions ---
$sourceArnRegions = "arn:aws:execute-api:${Region}:${accountId}:${apiId}/*/GET/api/regions"
aws lambda add-permission --function-name RiftRewindOrchestrator --statement-id apigateway-access-$(Get-Random) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArnRegions --region $Region 2>$null | Out-Null

# --- Enable CORS for /api/regions ---
Write-Host "[6b/6] Enabling CORS for /api/regions..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $regionsId --http-method OPTIONS --authorization-type NONE --region $Region 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $regionsId --http-method OPTIONS --type MOCK --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $regionsId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
$corsHeadersRegions = @{
    'method.response.header.Access-Control-Allow-Headers' = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    'method.response.header.Access-Control-Allow-Methods' = "'GET,OPTIONS'"
    'method.response.header.Access-Control-Allow-Origin' = "'*'"
}
$corsHeadersRegionsJson = $corsHeadersRegions | ConvertTo-Json -Compress
aws apigateway put-integration-response --rest-api-id $apiId --resource-id $regionsId --http-method OPTIONS --status-code 200 --response-parameters $corsHeadersRegionsJson --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $regionsId --http-method GET --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
Write-Host "OK CORS enabled for /api/regions" -ForegroundColor Green

# --- Create /api/health resource ---
Write-Host "[3d/6] Creating /api/health resource..." -ForegroundColor Yellow
$healthId = aws apigateway create-resource --rest-api-id $apiId --parent-id $apiResourceId --path-part health --region $Region --query 'id' --output text 2>$null
if (-not $healthId) {
    $healthId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query "items[?path=='/api/health'].id" --output text
    Write-Host "OK Resource already exists: $healthId" -ForegroundColor Green
} else {
    Write-Host "OK Resource created: $healthId" -ForegroundColor Green
}

# --- Add GET method to /api/health ---
Write-Host "[4c/6] Creating GET method for /api/health..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $healthId --http-method GET --authorization-type NONE --region $Region 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $healthId --http-method GET --type AWS_PROXY --integration-http-method POST --uri $lambdaUri --region $Region 2>$null | Out-Null
Write-Host "OK GET method configured" -ForegroundColor Green

# --- Enable CORS for /api/health ---
Write-Host "[6c/6] Enabling CORS for /api/health..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $healthId --http-method OPTIONS --authorization-type NONE --region $Region 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $healthId --http-method OPTIONS --type MOCK --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $healthId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
$corsHeadersHealth = @{
    'method.response.header.Access-Control-Allow-Headers' = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    'method.response.header.Access-Control-Allow-Methods' = "'GET,OPTIONS'"
    'method.response.header.Access-Control-Allow-Origin' = "'*'"
}
$corsHeadersHealthJson = $corsHeadersHealth | ConvertTo-Json -Compress
aws apigateway put-integration-response --rest-api-id $apiId --resource-id $healthId --http-method OPTIONS --status-code 200 --response-parameters $corsHeadersHealthJson --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $healthId --http-method GET --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
Write-Host "OK CORS enabled for /api/health" -ForegroundColor Green

# --- Create /api/rewind resource ---
Write-Host "[3e/6] Creating /api/rewind resource..." -ForegroundColor Yellow
$rewindId = aws apigateway create-resource --rest-api-id $apiId --parent-id $apiResourceId --path-part rewind --region $Region --query 'id' --output text 2>$null
if (-not $rewindId) {
    $rewindId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query "items[?path=='/api/rewind'].id" --output text
    Write-Host "OK Resource already exists: $rewindId" -ForegroundColor Green
} else {
    Write-Host "OK Resource created: $rewindId" -ForegroundColor Green
}

# --- Add POST method to /api/rewind ---
Write-Host "[4d/6] Creating POST method for /api/rewind..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $rewindId --http-method POST --authorization-type NONE --region $Region 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $rewindId --http-method POST --type AWS_PROXY --integration-http-method POST --uri $lambdaUri --region $Region 2>$null | Out-Null
Write-Host "OK POST method configured" -ForegroundColor Green

# --- Enable CORS for /api/rewind ---
Write-Host "[6d/6] Enabling CORS for /api/rewind..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $rewindId --http-method OPTIONS --authorization-type NONE --region $Region 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $rewindId --http-method OPTIONS --type MOCK --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $rewindId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
$corsHeadersRewind = @{
    'method.response.header.Access-Control-Allow-Headers' = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    'method.response.header.Access-Control-Allow-Methods' = "'POST,OPTIONS'"
    'method.response.header.Access-Control-Allow-Origin' = "'*'"
}
$corsHeadersRewindJson = $corsHeadersRewind | ConvertTo-Json -Compress
aws apigateway put-integration-response --rest-api-id $apiId --resource-id $rewindId --http-method OPTIONS --status-code 200 --response-parameters $corsHeadersRewindJson --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $rewindId --http-method POST --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
Write-Host "OK CORS enabled for /api/rewind" -ForegroundColor Green

# --- Create {sessionId} resource under /api/rewind ---
Write-Host "[3f/6] Creating {sessionId} resource..." -ForegroundColor Yellow
$sessionId = aws apigateway create-resource --rest-api-id $apiId --parent-id $rewindId --path-part "{sessionId}" --region $Region --query 'id' --output text 2>$null
if (-not $sessionId) {
    $sessionId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query "items[?path=='/api/rewind/{sessionId}'].id" --output text
    Write-Host "OK Resource already exists: $sessionId" -ForegroundColor Green
} else {
    Write-Host "OK Resource created: $sessionId" -ForegroundColor Green
}

# --- Add GET method to /api/rewind/{sessionId} ---
Write-Host "[4e/6] Creating GET method for /api/rewind/{sessionId}..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $sessionId --http-method GET --authorization-type NONE --region $Region --request-parameters "method.request.path.sessionId=true" 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $sessionId --http-method GET --type AWS_PROXY --integration-http-method POST --uri $lambdaUri --region $Region 2>$null | Out-Null
Write-Host "OK GET method configured" -ForegroundColor Green

# --- Enable CORS for /api/rewind/{sessionId} ---
Write-Host "[6e/6] Enabling CORS for /api/rewind/{sessionId}..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $sessionId --http-method OPTIONS --authorization-type NONE --region $Region --request-parameters "method.request.path.sessionId=true" 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $sessionId --http-method OPTIONS --type MOCK --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $sessionId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
$corsHeadersSession = @{
    'method.response.header.Access-Control-Allow-Headers' = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    'method.response.header.Access-Control-Allow-Methods' = "'GET,OPTIONS'"
    'method.response.header.Access-Control-Allow-Origin' = "'*'"
}
$corsHeadersSessionJson = $corsHeadersSession | ConvertTo-Json -Compress
aws apigateway put-integration-response --rest-api-id $apiId --resource-id $sessionId --http-method OPTIONS --status-code 200 --response-parameters $corsHeadersSessionJson --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $sessionId --http-method GET --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
Write-Host "OK CORS enabled for /api/rewind/{sessionId}" -ForegroundColor Green

# --- Create slide resource under /api/rewind/{sessionId} ---
Write-Host "[3g/6] Creating slide resource..." -ForegroundColor Yellow
$slideId = aws apigateway create-resource --rest-api-id $apiId --parent-id $sessionId --path-part slide --region $Region --query 'id' --output text 2>$null
if (-not $slideId) {
    $slideId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query "items[?path=='/api/rewind/{sessionId}/slide'].id" --output text
    Write-Host "OK Resource already exists: $slideId" -ForegroundColor Green
} else {
    Write-Host "OK Resource created: $slideId" -ForegroundColor Green
}

# --- Create {slideNumber} resource under slide ---
Write-Host "[3h/6] Creating {slideNumber} resource..." -ForegroundColor Yellow
$slideNumberId = aws apigateway create-resource --rest-api-id $apiId --parent-id $slideId --path-part "{slideNumber}" --region $Region --query 'id' --output text 2>$null
if (-not $slideNumberId) {
    $slideNumberId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query "items[?path=='/api/rewind/{sessionId}/slide/{slideNumber}'].id" --output text
    Write-Host "OK Resource already exists: $slideNumberId" -ForegroundColor Green
} else {
    Write-Host "OK Resource created: $slideNumberId" -ForegroundColor Green
}

# --- Add GET method to /api/rewind/{sessionId}/slide/{slideNumber} ---
Write-Host "[4f/6] Creating GET method for /api/rewind/{sessionId}/slide/{slideNumber}..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $slideNumberId --http-method GET --authorization-type NONE --region $Region --request-parameters "method.request.path.sessionId=true,method.request.path.slideNumber=true" 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $slideNumberId --http-method GET --type AWS_PROXY --integration-http-method POST --uri $lambdaUri --region $Region 2>$null | Out-Null
Write-Host "OK GET method configured" -ForegroundColor Green

# --- Enable CORS for /api/rewind/{sessionId}/slide/{slideNumber} ---
Write-Host "[6f/6] Enabling CORS for /api/rewind/{sessionId}/slide/{slideNumber}..." -ForegroundColor Yellow
aws apigateway put-method --rest-api-id $apiId --resource-id $slideNumberId --http-method OPTIONS --authorization-type NONE --region $Region --request-parameters "method.request.path.sessionId=true,method.request.path.slideNumber=true" 2>$null | Out-Null
aws apigateway put-integration --rest-api-id $apiId --resource-id $slideNumberId --http-method OPTIONS --type MOCK --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $slideNumberId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
$corsHeadersSlide = @{
    'method.response.header.Access-Control-Allow-Headers' = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    'method.response.header.Access-Control-Allow-Methods' = "'GET,OPTIONS'"
    'method.response.header.Access-Control-Allow-Origin' = "'*'"
}
$corsHeadersSlideJson = $corsHeadersSlide | ConvertTo-Json -Compress
aws apigateway put-integration-response --rest-api-id $apiId --resource-id $slideNumberId --http-method OPTIONS --status-code 200 --response-parameters $corsHeadersSlideJson --region $Region 2>$null | Out-Null
aws apigateway put-method-response --rest-api-id $apiId --resource-id $slideNumberId --http-method GET --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
Write-Host "OK CORS enabled for /api/rewind/{sessionId}/slide/{slideNumber}" -ForegroundColor Green

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
