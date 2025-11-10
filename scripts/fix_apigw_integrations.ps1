param(
    [string]$ApiId = "nqseqiylz5",
    [string]$Region = "us-east-1",
    [string]$LambdaFunctionName = "RiftRewindOrchestrator",
    [switch]$AutoApprove
)

Write-Host "Fix script for missing API Gateway integrations"
Write-Host "API: $ApiId  Region: $Region  Lambda function: $LambdaFunctionName`n"

# Load optional variables from scripts\apigw_vars.ps1 if present.
# Variables in that file use the APIGW_ prefix and are only applied when the
# corresponding CLI parameter was NOT provided (so CLI args remain highest priority).
$varsFile = Join-Path $PSScriptRoot 'apigw_vars.ps1'
if (Test-Path $varsFile) {
    try {
        . $varsFile
        Write-Host "Loaded variables from $varsFile" -ForegroundColor Green
        if (-not $PSBoundParameters.ContainsKey('ApiId') -and (Get-Variable -Name 'APIGW_ApiId' -Scope Script -ErrorAction SilentlyContinue)) { $ApiId = $APIGW_ApiId }
        if (-not $PSBoundParameters.ContainsKey('Region') -and (Get-Variable -Name 'APIGW_Region' -Scope Script -ErrorAction SilentlyContinue)) { $Region = $APIGW_Region }
        if (-not $PSBoundParameters.ContainsKey('LambdaFunctionName') -and (Get-Variable -Name 'APIGW_LambdaFunctionName' -Scope Script -ErrorAction SilentlyContinue)) { $LambdaFunctionName = $APIGW_LambdaFunctionName }
        if (-not $PSBoundParameters.ContainsKey('AutoApprove') -and (Get-Variable -Name 'APIGW_AutoApprove' -Scope Script -ErrorAction SilentlyContinue)) { if ($APIGW_AutoApprove) { $AutoApprove = $true } }
        if (Get-Variable -Name 'APIGW_LambdaArn' -Scope Script -ErrorAction SilentlyContinue) { $APIGW_LambdaArn_Present = $true }
    } catch {
        Write-Host "Warning: failed to load $varsFile - continuing with CLI/default values" -ForegroundColor Yellow
    }
}

# Resolve Lambda ARN (prefer explicit APIGW_LambdaArn if provided and no LambdaFunctionName was supplied)
if ($APIGW_LambdaArn_Present -and -not $PSBoundParameters.ContainsKey('LambdaFunctionName')) {
    $lambdaArn = $APIGW_LambdaArn
    Write-Host "Using Lambda ARN from vars file: $lambdaArn" -ForegroundColor Green
} else {
    $lambdaArn = aws lambda get-function --function-name $LambdaFunctionName --region $Region --query "Configuration.FunctionArn" --output text 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $lambdaArn) {
        Write-Host "ERROR: Could not find Lambda function '$LambdaFunctionName'. Please verify the function name and AWS credentials." -ForegroundColor Red
        exit 1
    }
    Write-Host "Found Lambda ARN: $lambdaArn`n" -ForegroundColor Green
}

# Fetch resources (handle multi-line/aws output in PowerShell returning an array)
$resourcesJsonRaw = aws apigateway get-resources --rest-api-id $ApiId --region $Region --output json 2>$null
if ($LASTEXITCODE -ne 0 -or -not $resourcesJsonRaw) {
    Write-Host "ERROR: Could not fetch resources for API $ApiId" -ForegroundColor Red
    exit 1
}

if ($resourcesJsonRaw -is [System.Object[]]) {
    $resourcesJson = $resourcesJsonRaw -join "`n"
} else {
    $resourcesJson = $resourcesJsonRaw
}

$resourcesObj = $null
try {
    $resourcesObj = ConvertFrom-Json $resourcesJson
} catch {
    Write-Host "ERROR: Failed to parse JSON from AWS CLI output." -ForegroundColor Red
    exit 1
}

# The AWS response has an 'items' array with the resources
$resources = $resourcesObj.items

$toFix = @()

foreach ($r in $resources) {
    if ($null -ne $r.resourceMethods) {
        foreach ($m in $r.resourceMethods.PSObject.Properties.Name) {
            # try to get integration
            aws apigateway get-integration --rest-api-id $ApiId --resource-id $r.id --http-method $m --region $Region > $null 2>$null
            if ($LASTEXITCODE -ne 0) {
                $toFix += [pscustomobject]@{ resourceId = $r.id; path = $r.path; method = $m }
            }
        }
    }
}

if ($toFix.Count -eq 0) {
    Write-Host "No missing integrations detected. Nothing to do." -ForegroundColor Green
    exit 0
}

Write-Host "Detected missing integrations:`n" -ForegroundColor Yellow
$toFix | Format-Table -AutoSize

if (-not $AutoApprove) {
    $confirm = Read-Host "Proceed to create integrations for the above items? (Y/N)"
    if ($confirm.ToUpper() -ne 'Y') {
        Write-Host "Aborting. No changes made." -ForegroundColor Cyan
        exit 0
    }
}

# For each missing integration, create appropriate integration
foreach ($item in $toFix) {
    $rid = $item.resourceId
    $method = $item.method
    $path = $item.path

    Write-Host "`nProcessing $method $path (resourceId: $rid)" -ForegroundColor Cyan

    if ($method -eq 'OPTIONS') {
        Write-Host " Creating OPTIONS method and MOCK integration (file-backed JSON) ..." -ForegroundColor Yellow

        # File paths
        $mockReqPath = Join-Path $PSScriptRoot 'mock_request.json'
        $methodRespParamsPath = Join-Path $PSScriptRoot 'method_response_parameters.json'
        $intRespParamsPath = Join-Path $PSScriptRoot 'integration_response_parameters.json'
        $intRespTemplatesPath = Join-Path $PSScriptRoot 'integration_response_templates.json'

        # Create canonical JSON files using .NET file write (UTF8, no BOM)
        [System.IO.File]::WriteAllText($mockReqPath, '{"application/json":"{\"statusCode\":200}"}', [System.Text.Encoding]::UTF8)

        $methodRespJson = '{"method.response.header.Access-Control-Allow-Origin": false, "method.response.header.Access-Control-Allow-Headers": false, "method.response.header.Access-Control-Allow-Methods": false}'
        [System.IO.File]::WriteAllText($methodRespParamsPath, $methodRespJson, [System.Text.Encoding]::UTF8)

        # Compute allowed methods for this resource
        $allowedMethods = "GET,POST,OPTIONS"
        try {
            $resMethodsRaw = aws apigateway get-resource --rest-api-id $ApiId --resource-id $rid --region $Region --query 'resourceMethods' --output text 2>$null
            if ($resMethodsRaw -is [System.Object[]]) { $resMethods = $resMethodsRaw -join "`n" } else { $resMethods = $resMethodsRaw }
            $resMethods = $resMethods -split "\s+"
            $methodsFound = @()
            foreach ($mname in $resMethods) {
                if ($mname -and $mname -ne 'NULL') { $methodsFound += $mname }
            }
            if ($methodsFound.Count -gt 0) { $allowedMethods = ($methodsFound -join ',') }
        } catch { }

        $intRespParamsContent = '{"method.response.header.Access-Control-Allow-Origin":"\"*\"","method.response.header.Access-Control-Allow-Headers":"\"Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token\"","method.response.header.Access-Control-Allow-Methods":"\"' + $allowedMethods + '\""}'
        [System.IO.File]::WriteAllText($intRespParamsPath, $intRespParamsContent, [System.Text.Encoding]::UTF8)

        $intRespTemplatesContent = '{"application/json":""}'
        [System.IO.File]::WriteAllText($intRespTemplatesPath, $intRespTemplatesContent, [System.Text.Encoding]::UTF8)

        # Put the method, integration and responses using file:// to avoid quoting issues
        aws apigateway put-method --rest-api-id $ApiId --resource-id $rid --http-method OPTIONS --authorization-type NONE --region $Region

        # Use absolute file:// paths
        $mockReqFull = (Resolve-Path $mockReqPath).ProviderPath
        $methodRespFull = (Resolve-Path $methodRespParamsPath).ProviderPath
        $intRespParamsFull = (Resolve-Path $intRespParamsPath).ProviderPath
        $intRespTemplatesFull = (Resolve-Path $intRespTemplatesPath).ProviderPath

        aws apigateway put-integration --rest-api-id $ApiId --resource-id $rid --http-method OPTIONS --type MOCK --request-templates file://$mockReqFull --region $Region

        aws apigateway put-method-response --rest-api-id $ApiId --resource-id $rid --http-method OPTIONS --status-code 200 --response-parameters file://$methodRespFull --region $Region

        aws apigateway put-integration-response --rest-api-id $ApiId --resource-id $rid --http-method OPTIONS --status-code 200 --selection-pattern "" --response-parameters file://$intRespParamsFull --response-templates file://$intRespTemplatesFull --region $Region

        if ($LASTEXITCODE -eq 0) {
            Write-Host " OPTIONS MOCK integration created for $path" -ForegroundColor Green
        } else {
            Write-Host " Warning: one or more AWS CLI calls returned non-zero exit code for resource $rid. Check output above." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host " Creating AWS_PROXY integration to Lambda ($LambdaFunctionName)..." -ForegroundColor Yellow
        $uri = "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${lambdaArn}/invocations"
        aws apigateway put-integration --rest-api-id $ApiId --resource-id $rid --http-method $method --type AWS_PROXY --integration-http-method POST --uri $uri --region $Region | Out-Null

        # Ensure method response includes CORS header for 200
        try {
            aws apigateway put-method-response --rest-api-id $ApiId --resource-id $rid --http-method $method --status-code 200 --response-parameters "method.response.header.Access-Control-Allow-Origin=false" --region $Region | Out-Null
        } catch { }

        Write-Host " $method integration created for $path" -ForegroundColor Green
    }
}

# Add Lambda permission for the API to invoke (if not already present)
# Build a generic source ARN to allow all stages/methods for this API
$accountId = aws sts get-caller-identity --query 'Account' --output text
$sourceArn = "arn:aws:execute-api:${Region}:${accountId}:${ApiId}/*/*/*"
$statementId = "apigw-access-${ApiId}-$(Get-Random)"
try {
    aws lambda add-permission --function-name $LambdaFunctionName --statement-id $statementId --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArn --region $Region | Out-Null
    Write-Host "Added Lambda permission statement: $statementId" -ForegroundColor Green
} catch {
    Write-Host "Warning: could not add Lambda permission (it may already exist)." -ForegroundColor Yellow
}

# Redeploy
Write-Host "`nCreating deployment to 'prod' stage..." -ForegroundColor Cyan
aws apigateway create-deployment --rest-api-id $ApiId --stage-name prod --region $Region --description "Fix missing integrations and add CORS mock" > $null 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment created and stage 'prod' updated." -ForegroundColor Green
} else {
    Write-Host "ERROR: Deployment failed. You may need to check for methods still missing integrations." -ForegroundColor Red
}

Write-Host "`nDone. Please re-test your OPTIONS request from the browser and run a full smoke test." -ForegroundColor Cyan
