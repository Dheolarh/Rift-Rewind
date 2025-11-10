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
        # Check if we need to redeploy - delete existing deployment
        $existingDeployment = aws apigateway get-deployments --rest-api-id $apiId --region $Region --query 'items[0].id' --output text 2>$null
        if ($existingDeployment) {
            Write-Host "Removing existing deployment to allow updates..." -ForegroundColor Yellow
            aws apigateway delete-deployment --rest-api-id $apiId --deployment-id $existingDeployment --region $Region 2>$null | Out-Null
        }
    } else {
        Write-Host "ERROR: Failed to create/find API" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "OK API created: $apiId" -ForegroundColor Green
}

# Function to ensure resource exists
function Ensure-Resource {
    param(
        [string]$ApiId,
        [string]$ParentId,
        [string]$PathPart,
        [string]$Region
    )

    $existingResource = aws apigateway get-resources --rest-api-id $ApiId --region $Region --query "items[?pathPart=='$PathPart' && parentId=='$ParentId'].id" --output text 2>$null
    if ($existingResource -and $existingResource -ne "None") {
        Write-Host "OK Resource '$PathPart' already exists: $existingResource" -ForegroundColor Green
        return $existingResource
    }

    $newResource = aws apigateway create-resource --rest-api-id $ApiId --parent-id $ParentId --path-part $PathPart --region $Region --query 'id' --output text 2>$null
    if ($newResource) {
        Write-Host "OK Resource '$PathPart' created: $newResource" -ForegroundColor Green
        return $newResource
    }

    Write-Host "ERROR: Failed to create/find resource '$PathPart'" -ForegroundColor Red
    exit 1
}

# Function to ensure method exists
function Ensure-Method {
    param(
        [string]$ApiId,
        [string]$ResourceId,
        [string]$HttpMethod,
        [string]$Region,
        [string]$RequestParameters = ""
    )

    # Check if method exists
    $methodExists = aws apigateway get-method --rest-api-id $ApiId --resource-id $ResourceId --http-method $HttpMethod --region $Region 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Method $HttpMethod already exists" -ForegroundColor Green
        return
    }

    # Create method
    if ($RequestParameters) {
        aws apigateway put-method --rest-api-id $ApiId --resource-id $ResourceId --http-method $HttpMethod --authorization-type NONE --region $Region --request-parameters $RequestParameters 2>$null | Out-Null
    } else {
        aws apigateway put-method --rest-api-id $ApiId --resource-id $ResourceId --http-method $HttpMethod --authorization-type NONE --region $Region 2>$null | Out-Null
    }
    Write-Host "OK Method $HttpMethod created" -ForegroundColor Green
}

# Function to ensure integration exists
function Ensure-Integration {
    param(
        [string]$ApiId,
        [string]$ResourceId,
        [string]$HttpMethod,
        [string]$LambdaUri,
        [string]$Region
    )

    # Check if integration exists
    $integrationExists = aws apigateway get-integration --rest-api-id $ApiId --resource-id $ResourceId --http-method $HttpMethod --region $Region 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Integration $HttpMethod already exists" -ForegroundColor Green
        return
    }

    # Create integration
    aws apigateway put-integration --rest-api-id $ApiId --resource-id $ResourceId --http-method $HttpMethod --type AWS_PROXY --integration-http-method POST --uri $LambdaUri --region $Region 2>$null | Out-Null
    Write-Host "OK Integration $HttpMethod created" -ForegroundColor Green
}

# Function to enable CORS for a resource
function Enable-CORS {
    param(
        [string]$ApiId,
        [string]$ResourceId,
        [string]$AllowedMethods,
        [string]$Region,
        [string]$RequestParameters = ""
    )

    # Create OPTIONS method
    if ($RequestParameters) {
        aws apigateway put-method --rest-api-id $ApiId --resource-id $ResourceId --http-method OPTIONS --authorization-type NONE --region $Region --request-parameters $RequestParameters 2>$null | Out-Null
    } else {
        aws apigateway put-method --rest-api-id $ApiId --resource-id $ResourceId --http-method OPTIONS --authorization-type NONE --region $Region 2>$null | Out-Null
    }

    # Create MOCK integration for OPTIONS
    aws apigateway put-integration --rest-api-id $ApiId --resource-id $ResourceId --http-method OPTIONS --type MOCK --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $Region 2>$null | Out-Null

    # Create method response for OPTIONS
    aws apigateway put-method-response --rest-api-id $ApiId --resource-id $ResourceId --http-method OPTIONS --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null

    # Create integration response for OPTIONS
    $corsHeaders = @{
        'method.response.header.Access-Control-Allow-Headers' = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
        'method.response.header.Access-Control-Allow-Methods' = "'$AllowedMethods'"
        'method.response.header.Access-Control-Allow-Origin' = "'*'"
    }
    $corsHeadersJson = $corsHeaders | ConvertTo-Json -Compress
    aws apigateway put-integration-response --rest-api-id $ApiId --resource-id $ResourceId --http-method OPTIONS --status-code 200 --response-parameters $corsHeadersJson --region $Region 2>$null | Out-Null

    # Add CORS headers to actual method responses
    $methods = $AllowedMethods -split ','
    foreach ($method in $methods) {
        if ($method -ne 'OPTIONS') {
            aws apigateway put-method-response --rest-api-id $ApiId --resource-id $ResourceId --http-method $method --status-code 200 --response-parameters 'method.response.header.Access-Control-Allow-Origin=false' --region $Region 2>$null | Out-Null
        }
    }

    Write-Host "OK CORS enabled for $AllowedMethods" -ForegroundColor Green
}

# Get root resource ID
$rootId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query 'items[?path==`/`].id' --output text

# Set Lambda URI
$lambdaUri = "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/$lambdaArn/invocations"

# Create /analyze endpoint
Write-Host "[3/6] Setting up /analyze endpoint..." -ForegroundColor Yellow
$analyzeId = Ensure-Resource -ApiId $apiId -ParentId $rootId -PathPart "analyze" -Region $Region
Ensure-Method -ApiId $apiId -ResourceId $analyzeId -HttpMethod "POST" -Region $Region
Ensure-Integration -ApiId $apiId -ResourceId $analyzeId -HttpMethod "POST" -LambdaUri $lambdaUri -Region $Region
Enable-CORS -ApiId $apiId -ResourceId $analyzeId -AllowedMethods "POST,OPTIONS" -Region $Region

# Create /api endpoints
Write-Host "[4/6] Setting up /api/* endpoints..." -ForegroundColor Yellow
$apiResourceId = Ensure-Resource -ApiId $apiId -ParentId $rootId -PathPart "api" -Region $Region

# /api/health
$healthId = Ensure-Resource -ApiId $apiId -ParentId $apiResourceId -PathPart "health" -Region $Region
Ensure-Method -ApiId $apiId -ResourceId $healthId -HttpMethod "GET" -Region $Region
Ensure-Integration -ApiId $apiId -ResourceId $healthId -HttpMethod "GET" -LambdaUri $lambdaUri -Region $Region
Enable-CORS -ApiId $apiId -ResourceId $healthId -AllowedMethods "GET,OPTIONS" -Region $Region

# /api/regions
$regionsId = Ensure-Resource -ApiId $apiId -ParentId $apiResourceId -PathPart "regions" -Region $Region
Ensure-Method -ApiId $apiId -ResourceId $regionsId -HttpMethod "GET" -Region $Region
Ensure-Integration -ApiId $apiId -ResourceId $regionsId -HttpMethod "GET" -LambdaUri $lambdaUri -Region $Region
Enable-CORS -ApiId $apiId -ResourceId $regionsId -AllowedMethods "GET,OPTIONS" -Region $Region

# /api/rewind
$rewindId = Ensure-Resource -ApiId $apiId -ParentId $apiResourceId -PathPart "rewind" -Region $Region
Ensure-Method -ApiId $apiId -ResourceId $rewindId -HttpMethod "POST" -Region $Region
Ensure-Integration -ApiId $apiId -ResourceId $rewindId -HttpMethod "POST" -LambdaUri $lambdaUri -Region $Region
Enable-CORS -ApiId $apiId -ResourceId $rewindId -AllowedMethods "POST,OPTIONS" -Region $Region

# /api/rewind/{sessionId}
$sessionIdResource = Ensure-Resource -ApiId $apiId -ParentId $rewindId -PathPart "{sessionId}" -Region $Region
Ensure-Method -ApiId $apiId -ResourceId $sessionIdResource -HttpMethod "GET" -Region $Region -RequestParameters "method.request.path.sessionId=true"
Ensure-Integration -ApiId $apiId -ResourceId $sessionIdResource -HttpMethod "GET" -LambdaUri $lambdaUri -Region $Region
Enable-CORS -ApiId $apiId -ResourceId $sessionIdResource -AllowedMethods "GET,OPTIONS" -Region $Region -RequestParameters "method.request.path.sessionId=true"

# /api/rewind/{sessionId}/slide/{slideNumber}
$slideId = Ensure-Resource -ApiId $apiId -ParentId $sessionIdResource -PathPart "slide" -Region $Region
$slideNumberId = Ensure-Resource -ApiId $apiId -ParentId $slideId -PathPart "{slideNumber}" -Region $Region
Ensure-Method -ApiId $apiId -ResourceId $slideNumberId -HttpMethod "GET" -Region $Region -RequestParameters "method.request.path.sessionId=true,method.request.path.slideNumber=true"
Ensure-Integration -ApiId $apiId -ResourceId $slideNumberId -HttpMethod "GET" -LambdaUri $lambdaUri -Region $Region
Enable-CORS -ApiId $apiId -ResourceId $slideNumberId -AllowedMethods "GET,OPTIONS" -Region $Region -RequestParameters "method.request.path.sessionId=true,method.request.path.slideNumber=true"

# Add Lambda permissions for all endpoints
Write-Host "`n[6/6] Adding Lambda permissions for all endpoints..." -ForegroundColor Yellow

# Permission for /analyze
$sourceArnAnalyze = "arn:aws:execute-api:${Region}:${accountId}:${apiId}/*/POST/analyze"
aws lambda add-permission --function-name RiftRewindOrchestrator --statement-id apigateway-access-analyze-$(Get-Random) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArnAnalyze --region $Region 2>$null | Out-Null

# Permission for /api/health
$sourceArnHealth = "arn:aws:execute-api:${Region}:${accountId}:${apiId}/*/GET/api/health"
aws lambda add-permission --function-name RiftRewindOrchestrator --statement-id apigateway-access-health-$(Get-Random) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArnHealth --region $Region 2>$null | Out-Null

# Permission for /api/regions
$sourceArnRegions = "arn:aws:execute-api:${Region}:${accountId}:${apiId}/*/GET/api/regions"
aws lambda add-permission --function-name RiftRewindOrchestrator --statement-id apigateway-access-regions-$(Get-Random) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArnRegions --region $Region 2>$null | Out-Null

# Permission for /api/rewind
$sourceArnRewind = "arn:aws:execute-api:${Region}:${accountId}:${apiId}/*/POST/api/rewind"
aws lambda add-permission --function-name RiftRewindOrchestrator --statement-id apigateway-access-rewind-$(Get-Random) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArnRewind --region $Region 2>$null | Out-Null

# Permission for /api/rewind/{sessionId}
$sourceArnSession = "arn:aws:execute-api:${Region}:${accountId}:${apiId}/*/GET/api/rewind/*"
aws lambda add-permission --function-name RiftRewindOrchestrator --statement-id apigateway-access-session-$(Get-Random) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArnSession --region $Region 2>$null | Out-Null

# Permission for /api/rewind/{sessionId}/slide/{slideNumber}
$sourceArnSlide = "arn:aws:execute-api:${Region}:${accountId}:${apiId}/*/GET/api/rewind/*/slide/*"
aws lambda add-permission --function-name RiftRewindOrchestrator --statement-id apigateway-access-slide-$(Get-Random) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArnSlide --region $Region 2>$null | Out-Null

Write-Host "OK Lambda permissions added for all endpoints" -ForegroundColor Green

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
