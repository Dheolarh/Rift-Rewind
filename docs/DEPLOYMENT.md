# Deployment Guide — Backend (AWS)

This guide describes how to package and deploy the backend Lambda functions for Rift Rewind, configure S3 and IAM, set environment variables, and wire API Gateway endpoints. It assumes you have AWS CLI configured and PowerShell available (Windows).

Summary of the Lambda functions to create

- Function name: rewind.orchestrator
	- Handler: `lambdas.orchestrator.lambda_handler`
	- Purpose: quick account lookup, write `sessions/{sessionId}/raw_data.json` to S3, return sessionId, and invoke the processor Lambda asynchronously.

- Function name: rewind.processor
	- Handler: `lambdas.processor.lambda_handler`
	- Purpose: download `raw_data.json`, fetch matches if needed, run analytics, call Bedrock to generate humor/insights, upload `analytics.json` and per-slide humor to S3, write cache and status updates.

Note: The handler module paths above (lambdas.orchestrator / lambdas.processor) should match how you package the `backend` code into the Lambda zip. If you package using the `backend/` root as the module root, the `lambdas` package should be available in the zip and the handlers will resolve correctly.

Prerequisites

- AWS CLI configured with credentials and default region.
- Python 3.11+ locally to install dependencies for packaging (if required).
- An S3 bucket to store session and cache data. Set the name as `S3_BUCKET_NAME` in Lambda env (example: `rift-rewind-sessions`).
- The Bedrock model id you will use. For this project set:

```
BEDROCK_MODEL_ID=meta us.meta.llama3-1-70b-instruct-v1:0
```

- (Optional) A packaging script `package_lambdas.ps1`

S3 configuration

1. Create the bucket (or reuse an existing one):

```powershell
aws s3api create-bucket --bucket rift-rewind-sessions --region us-east-1 --create-bucket-configuration LocationConstraint=us-east-1
```

2. Ensure the Lambda roles have access to the bucket (see IAM section below).

Packaging the Lambda code

If you already have a `backend/package_lambdas.ps1` script, run it from the repository `backend` folder. The script typically installs dependencies and zips the python modules into a deployable archive for each Lambda.


Create the Lambda functions (AWS CLI)

Below are example commands to create the two Lambda functions. Replace account/region/bucket names as appropriate.

1. Create an IAM role for the Lambdas (or use existing roles). Minimal role trust policy for Lambda:

```powershell
$trust = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
aws iam create-role --role-name rift-rewind-lambda-role --assume-role-policy-document $trust

# Attach basic execution policy for CloudWatch logs
aws iam attach-role-policy --role-name rift-rewind-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

2. Create the processor Lambda (example):

```powershell
$bucketZip = 'my-deploy-bucket' # optional: upload zips to S3 and refer by S3Key
aws lambda create-function --function-name rewind.processor `
	--runtime python3.10 `
	--role arn:aws:iam::123456789012:role/rift-rewind-lambda-role `
	--handler lambdas.processor.lambda_handler `
	--zip-file fileb://backend/dist/rewind-processor.zip `
	--timeout 900 --memory-size 2048
```

3. Create the orchestrator Lambda (example):

```powershell
aws lambda create-function --function-name rewind.orchestrator `
	--runtime python3.10 `
	--role arn:aws:iam::123456789012:role/rift-rewind-lambda-role `
	--handler lambdas.orchestrator.lambda_handler `
	--zip-file fileb://backend/dist/rewind-orchestrator.zip `
	--timeout 60 --memory-size 512
```

Environment variables and configuration

Set the following environment variables on both or the appropriate Lambdas (configure via Console or AWS CLI --update-function-configuration):

- `S3_BUCKET_NAME` — the bucket name for sessions and cache
- `BEDROCK_MODEL_ID` — us.meta.llama3-1-70b-instruct-v1:0
- `RIOT_API_KEY` — RGAPXXXXXXXXXXXXXXX
- `SESSION_EXPIRY_HOURS` — 	hours you want to store player details for on S3 (72)
- `MAX_MATCHES_TO_FETCH` — number of max player matches to fetch
- `TEST_MODE` — false

Example update env command (PowerShell):

```powershell
aws lambda update-function-configuration --function-name rewind.orchestrator --environment Variables=@{S3_BUCKET_NAME='rift-rewind-sessions';PROCESSOR_LAMBDA_NAME='rewind.processor';BEDROCK_MODEL_ID='meta us.meta.llama3-1-70b-instruct-v1:0';AWS_DEFAULT_REGION='us-east-1'}
```

IAM permissions required

- Orchestrator must be able to:
	- s3:PutObject (to write sessions/{sessionId}/raw_data.json and status)
	- s3:GetObject (to read raw_data if needed)
	- lambda:InvokeFunction (to invoke the processor)

- Processor must be able to:
	- s3:GetObject, s3:PutObject (to read raw_data and write analytics/humor/status)
	- bedrock:InvokeModel (to call Bedrock models)
	- logs:CreateLogStream, logs:PutLogEvents

Attach a policy similar to the example in `docs/AWS_ARCHITECTURE.md` and scope resources to your S3 bucket and Bedrock model ARNs.

API Gateway setup

The API exposes the following endpoints. You can create an HTTP API or REST API in API Gateway and point routes to the orchestrator Lambda (rewind.orchestrator) or integrate with Lambda proxy for all endpoints.

Required routes and methods:

- GET  /api/health
- GET  /api/regions
- POST /api/rewind
- GET  /api/rewind/{sessionId}
- GET  /api/rewind/{sessionId}/slide/{slideNumber}
- POST /api/cache/check
- POST /api/cache/invalidate

Mapping suggestions

- Use a single Lambda proxy integration (rewind.orchestrator) that internally dispatches routes when run in Lambda (the project includes an API wrapper that mimics API Gateway behavior). If you prefer separate Lambda handlers for different endpoints, create small wrapper Lambdas that call into the orchestrator code.

Example (create an HTTP API and add a Lambda integration) — PowerShell/AWS CLI sample

```powershell
# Create HTTP API
$apiId = (aws apigatewayv2 create-api --name "rift-rewind-api" --protocol-type HTTP | ConvertFrom-Json).ApiId

# Create integration to orchestrator
$integrationId = (aws apigatewayv2 create-integration --api-id $apiId --integration-type AWS_PROXY --integration-uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:rewind.orchestrator/invocations | ConvertFrom-Json).IntegrationId

# Create routes for the endpoints
aws apigatewayv2 create-route --api-id $apiId --route-key "GET /api/health" --target "integrations/$integrationId"
aws apigatewayv2 create-route --api-id $apiId --route-key "GET /api/regions" --target "integrations/$integrationId"
aws apigatewayv2 create-route --api-id $apiId --route-key "POST /api/rewind" --target "integrations/$integrationId"
aws apigatewayv2 create-route --api-id $apiId --route-key "GET /api/rewind/{sessionId}" --target "integrations/$integrationId"
aws apigatewayv2 create-route --api-id $apiId --route-key "GET /api/rewind/{sessionId}/slide/{slideNumber}" --target "integrations/$integrationId"
aws apigatewayv2 create-route --api-id $apiId --route-key "POST /api/cache/check" --target "integrations/$integrationId"
aws apigatewayv2 create-route --api-id $apiId --route-key "POST /api/cache/invalidate" --target "integrations/$integrationId"

# Deploy the API
aws apigatewayv2 create-deployment --api-id $apiId --description "Initial deployment"
# Create stage $default
aws apigatewayv2 create-stage --api-id $apiId --stage-name prod --auto-deploy

# Allow API Gateway to invoke the Lambda
aws lambda add-permission --function-name rewind.orchestrator --statement-id apigw-invoke --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn arn:aws:execute-api:us-east-1:123456789012:$apiId/*/*/
```

Note: update ARNs and account IDs to match your environment. The `add-permission` call should include the exact execute-api ARN or a suitable pattern.

Testing the deployment

- Health check:
```powershell
Invoke-RestMethod -Method Get -Uri "https://<api-gateway-url>/api/health"
```

- Start a rewind (sample):
```powershell
$body = @{ gameName = 'SummonerName'; tagLine = 'TAG'; region = 'tr1'} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://<api-gateway-url>/api/rewind" -Body $body -ContentType 'application/json'
```

- Poll the session:
```powershell
Invoke-RestMethod -Method Get -Uri "https://<api-gateway-url>/api/rewind/<sessionId>"
```

S3 paths to inspect for debugging

- sessions/{sessionId}/status.json — processing status and messages
- sessions/{sessionId}/raw_data.json — initial fetcher data
- sessions/{sessionId}/analytics.json — analytics output
- sessions/{sessionId}/humor/slide_{n}.json — per-slide humor
- cache/users/{safe_name}/metadata.json — cache metadata (matchCount/totalMatches)

Frontend hosting (Amplify)

- Push the frontend changes (Vite build) to the repository connected to Amplify. Configure build settings to run `npm install` and `npm run build`, with publish directory `dist`.

Troubleshooting notes

- If orchestrator returns cached results with zeros for match counts: check `cache/users/{safe_name}/metadata.json` in S3 to see what was saved and check processor logs for `No matches in raw_data - fetching match history` messages.
- If API Gateway returns 502/500: check orchestrator Lambda CloudWatch logs for stack traces.
- If processor never runs: verify `PROCESSOR_LAMBDA_NAME` env var on orchestrator and that the orchestrator role has `lambda:InvokeFunction` permission for the processor ARN.
