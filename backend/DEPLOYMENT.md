# Deployment Guide — Rift Rewind Backend & Frontend

This document explains how to package the backend Lambda functions and configure the frontend to call your API Gateway.

## Overview
- Backend lambdas: `orchestrator`, `humor_context`, `insights`, `league_data` (files in `backend/lambdas`). Each exposes a `lambda_handler` function.
- Frontend uses `VITE_API_BASE_URL` (or `VITE_API_ENDPOINT`) to call the API.

## 1) Package Lambda functions
A PowerShell packaging script is provided: `backend/package_lambdas.ps1`.

Usage (Windows PowerShell):

```powershell
# From repository root
powershell -ExecutionPolicy Bypass -File backend\package_lambdas.ps1
```

The script will create zip files in `backend/lambda_packages` named `orchestrator.zip`, `humor_context.zip`, `insights.zip`, `league_data.zip`.

What it does:
- Creates a temporary build folder
- Installs Python dependencies from `backend/requirements.txt` into the package (uses `python -m pip install -r ... -t package`)
- Copies the specific lambda file (`backend/lambdas/<lambda>.py`) and the `backend/services` package into the build
- Zips the combined contents into `backend/lambda_packages/<lambda>.zip`

Notes and tips:
- The script assumes a system `python` is available on PATH. If your environment uses `python3` or a virtualenv, pass the `-Python` parameter or adjust script.
- If you prefer Lambda Layers for dependencies, modify the packaging to only include your code, and create a layer with the `site-packages` contents.
- If any extra backend modules are imported by lambdas, ensure they are copied into the zip (the script attempts to include `backend/api.py` and `backend/server.py` if present).

## 2) Create Lambda functions in AWS
For each zip created:
- Console: Create a new Lambda function (Python 3.11 recommended).
- Runtime handler: `<lambda_filename>.lambda_handler` (e.g., `orchestrator.lambda_handler`).
- Upload the zip as the function code.
- Set environment variables required by the lambda (see `.env` or your deployment secrets): `S3_BUCKET_NAME`, `BEDROCK_MODEL_ID`, any AWS credentials are provided by IAM role assigned to Lambda.
- IAM role: grant S3 Get/Put, CloudWatch logs, and any other services (Bedrock access if using AWS accounts that require policies).

Alternatively, use SAM/CloudFormation to create functions and integrate with API Gateway.

## 3) API Gateway
The API paths expected by the frontend are:

```
/api/health (GET)
/api/regions (GET)
/api/rewind (POST)
/api/rewind/{sessionId} (GET)
/api/rewind/{sessionId}/slide/{slideNumber} (GET)
/api/cache/check (POST)
/api/cache/invalidate (POST)
```

- Create a REST API or HTTP API in API Gateway.
- Integrate each path with the appropriate Lambda (method-level integration). For REST API, you can enable proxying and route all `/api/*` to the `orchestrator` function which already inspects the path, but the orchestrator expects to be the API entrypoint (see `backend/lambdas/orchestrator.py`). If you prefer finer-grained routing, set up methods and map to respective lambdas.
- Deploy the API to a stage (e.g., `prod`) and note the invoke URL.

Example base URL:
```
https://{api_id}.execute-api.{region}.amazonaws.com/{stage}
```
Then your frontend `VITE_API_BASE_URL` should be set to:
```
https://{api_id}.execute-api.{region}.amazonaws.com/{stage}/api
```

## 4) Frontend (Amplify) configuration
- In Amplify Console, connect your GitHub repo and branch.
- In Build settings, ensure environment variables are set:
  - `VITE_API_BASE_URL` = `https://{api_id}.execute-api.{region}.amazonaws.com/{stage}/api`
- Amplify build command usually uses `npm run build` or `yarn build`. Confirm `package.json` scripts.
- After deploy, the frontend will call the API endpoints using `frontend/src/services/api.ts` which respects `VITE_API_BASE_URL`.

## 5) Testing
- After Lambda and API Gateway are deployed, call `GET {VITE_API_BASE_URL}/health` in a browser or curl to confirm the backend responds.
- Start a rewind via `POST {VITE_API_BASE_URL}/rewind` with body `{ "gameName": "name", "tagLine": "#0000", "region": "na1" }`.

Async Processor Lambda
----------------------
This project now uses an async processor Lambda to run the heavy analysis outside the orchestrator handler.

Configuration:
- Set environment variable `PROCESSOR_LAMBDA_NAME` on the orchestrator Lambda (or in your local `.env`) to the deployed name of the processor Lambda (default: `rift-rewind-processor`).

IAM:
- The orchestrator Lambda must be granted permission to invoke the processor Lambda. Example minimal IAM policy to attach to the orchestrator's role:

```json
{
  "Effect": "Allow",
  "Action": "lambda:InvokeFunction",
  "Resource": "arn:aws:lambda:<region>:<account-id>:function:<processor-function-name>"
}
```

- The processor Lambda needs S3 read/write access for the sessions bucket and permission to write logs. Ensure its role includes S3 access (GetObject/PutObject/DeleteObject) on the `S3_BUCKET_NAME` you use.

Notes:
- The orchestrator uploads `sessions/{sessionId}/raw_data.json` to S3 and then asynchronously invokes the processor Lambda with a small payload containing the S3 key. This avoids payload-size limits on Lambda.invoke.
- If you prefer Step Functions or SQS-driven processing for more visibility/retries, consider migrating later; this async-Lambda approach is a compact, low-friction fix.
- Poll the session and slide endpoints as the frontend would.

## 6) Troubleshooting
- If Lambdas fail due to missing dependencies or import errors, consider packaging into a Lambda Layer or trimming imports.
- Use CloudWatch logs to see full tracebacks. The code uses `logger.exception` for helpful traces.

## 7) Optional improvements
- Create a CloudFormation or SAM template to automate function creation and API Gateway integration.
- Move large dependencies (e.g., Bedrock/LLM helper libraries) into layers.
- Add health checks and IAM least-privilege roles.

---
If you'd like, I can:
- Add a SAM template that defines the 4 Lambdas and the API Gateway with routes.
- Update the frontend components to prefer `humor/slide_{n}.json` headlines (so they fetch shorter payloads). 

Tell me which you'd like next and I will implement it.
