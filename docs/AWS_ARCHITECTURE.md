# Rift Rewind — AWS Architecture

This document describes the AWS architecture used by the Rift Rewind project. It covers the services used, the roles and permissions, communication and data flow, AI components, storage and caching, API surface and hosting, monitoring, security and recommended deployment steps.

## High-level overview

- Frontend: Vite + React app hosted on AWS Amplify (serves static files, CloudFront + S3 under the hood).
- Backend: AWS Lambda functions behind API Gateway (orchestrator + auxiliary lambdas). Lambdas perform fetches from Riot APIs, compute analytics, and invoke AI systems for humor/insights.
- Storage: S3 bucket used for session storage (`sessions/{sessionId}/...`) and cached sessions (`cache/users/...`).
- Async processing: Orchestrator uploads raw fetch data to S3 and invokes a processor Lambda asynchronously to run heavy analytics and AI generation.
- AI: AWS Bedrock — the project is configured to call Bedrock for AI generation. The code reads `BEDROCK_MODEL_ID` from environment variables; `InsightsGenerator` and `HumorGenerator` call the configured Bedrock model endpoint.
- Monitoring: CloudWatch Logs and metrics for Lambdas; S3 access logs optional.

## AWS Services used

- AWS Lambda — compute for backend lambdas (orchestrator, processor, other helpers).
- Amazon API Gateway — public HTTP endpoints that front the orchestrator Lambda.
- Amazon S3 — persistent storage for raw fetcher data, analytics.json, insights.json, per-slide humor JSON, session `status.json`, and cache data.
- AWS Amplify — hosting for the frontend static site.
- AWS CloudWatch — logs, metrics, and alarms for Lambdas and other services.
- AWS IAM — roles and policies for least-privilege access between services.
 - AWS Bedrock — AI model endpoint used by `InsightsGenerator` and `HumorGenerator`.

## Main components and responsibilities

- Orchestrator Lambda (`backend/api.py` / start_rewind):
  - Validates input and performs an initial quick lookup (ACCOUNT-V1 / SUMMONER-V4 / LEAGUE-V4) to confirm the player exists.
  - Builds a short `player_info` object and writes an initial `sessions/{sessionId}/status.json` (status `found`).
  - Uploads `sessions/{sessionId}/raw_data.json` (the fetcher data containing account/summoner/ranked and optionally initial matches) to S3.
  - Invokes the Processor Lambda asynchronously (InvocationType='Event') with a minimal payload that references the S3 `raw_data.json` key.

- Processor Lambda (`backend/lambdas/processor.py`):
  - Downloads `raw_data.json` from S3 and, if necessary, fetches the full match history and match details using the same `LeagueDataFetcher` logic.
  - Runs analytics (via `RiftRewindAnalytics`) to compute per-slide analytics.
  - Invokes AI generators (`HumorGenerator`, `InsightsGenerator`) to produce slide humor and coaching insights.
  - Uploads `analytics.json`, per-slide `humor/slide_{n}.json`, `insights.json` and updates `sessions/{sessionId}/status.json` with progress updates.
  - Persists a complete cached session at `cache/users/{safe_name}/complete_session.json` and `metadata.json` (for quick cache checks).

- Session cache — S3-based caching layer (`services/session_cache.py`):
  - Stores a per-user cached session with metadata including `matchCount`, `totalMatches`, `cachedAt`, and expiry.
  - `get_cached_session` and `find_session_by_id` are used by the orchestrator and get endpoints.

## Data flow / communication patterns

1. Frontend POST /api/rewind → API Gateway → Orchestrator Lambda.
2. Orchestrator performs a quick fetcher lookup (account, summoner, ranked).
3. Orchestrator writes `sessions/{sessionId}/raw_data.json` to S3 containing the fetcher data.
4. Orchestrator invokes Processor Lambda asynchronously, passing { session_id, raw_data_s3_key, game_name, tag_line, region }.
5. Processor Lambda downloads `raw_data.json` from S3. If `matches` are absent or empty, it will fetch match IDs and match details (no sampling) using `LeagueDataFetcher`.
6. Processor runs analytics, uploads `analytics.json` and generates per-slide humor files and `insights.json` (calls AI endpoints as configured).
7. Processor updates `sessions/{sessionId}/status.json` at each major step to allow the frontend to poll for progress.
8. Processor saves a full cached session (if desired) under `cache/users/{safe_name}/complete_session.json` and `metadata.json` for quick future lookups.

## S3 layout (convention)

- sessions/{sessionId}/
  - raw_data.json
  - status.json
  - analytics.json
  - insights.json
  - humor/slide_{n}.json

- cache/users/{safe_name}/
  - complete_session.json
  - metadata.json

Notes
- Keep the S3 bucket name consistent via env var `S3_BUCKET_NAME`. The code expects this; set in Lambda environment variables and deployment configs.

## IAM roles and minimal privileges

Recommended roles (least privilege):

- Orchestrator Lambda role
  - Permissions:
    - s3:PutObject, s3:GetObject, s3:ListBucket on the sessions bucket (for status/raw upload).
    - lambda:InvokeFunction on the Processor Lambda (if invoking by name/ARN).
    - logs:CreateLogStream, logs:PutLogEvents for CloudWatch.

 - Processor Lambda role
  - Permissions:
    - s3:GetObject, s3:PutObject on the sessions bucket and cache prefix.
    - logs:CreateLogStream, logs:PutLogEvents for CloudWatch.
    - (Optional) kms:Decrypt if S3 objects are encrypted with a KMS key.
    - If the Processor calls Bedrock, grant minimal Bedrock permissions (see Bedrock role below).

 - Bedrock execution role
   - IAM permissions to invoke Bedrock model endpoints.
   - Example actions: `bedrock:InvokeModel`, `bedrock:DescribeModel` scoped to the model ARN or resource.

Example minimal policy JSON for Orchestrator (attach to its role):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": [
        "arn:aws:lambda:REGION:ACCOUNT_ID:function:your-processor-function"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## AI system integration

- This project uses AWS Bedrock for AI generation. The backend reads the Bedrock model identifier from the `BEDROCK_MODEL_ID` environment variable. Set this variable to your chosen Bedrock model; for this deployment use:

```
BEDROCK_MODEL_ID=meta us.meta.llama3-1-70b-instruct-v1:0
```

- The `InsightsGenerator` and `HumorGenerator` modules call Bedrock to produce JSON outputs (headlines, strengths/weaknesses, per-slide humor text). AI calls are made from the Processor Lambda so the orchestrator remains low-latency and the heavy work is done asynchronously.

- Bedrock permissions: the Processor Lambda (or a dedicated Bedrock execution role) needs permission to invoke Bedrock models. Grant minimal privileges such as `bedrock:InvokeModel` and `bedrock:DescribeModel` scoped to the model resources in your account/region.

## Caching strategy

- Short-term status: `sessions/{sessionId}/status.json` tracks the current processing state so the frontend can poll.
- Long-term cache: `cache/users/{safe_name}/complete_session.json` stores complete session outputs + `metadata.json` with `matchCount`, `totalMatches`, `cachedAt`, and expiry.
- Cache expiry: default 7 days (configurable in `SessionCacheManager`). The orchestrator checks the cache before fetching new data.

## API surface

- POST /api/rewind — start a session (returns sessionId immediately; orchestrator returns cached results if available).
- GET /api/rewind/{sessionId} — poll for session status or get analytics/humor when ready.
- GET /api/rewind/{sessionId}/slide/{slideNumber} — get a single slide data (analytics + humor) — useful for incremental loading.
- GET /api/regions — get available regions list for the frontend.

Security: Use API Gateway authorizers (optional) if you want to restrict usage or add rate-limiting and API keys.

## Hosting & CDN

- Frontend is deployed to Amplify. Amplify automatically builds the Vite app and serves static assets via CloudFront.
- Static asset paths are content-hashed by Vite;

## Monitoring & Observability

- CloudWatch Logs: All Lambdas should write logs and structured events for key lifecycle events (session created, raw_data uploaded, processor started/completed/failed, AI errors).
- CloudWatch Alarms: Set alarms on Lambda error rates and throttles and on S3 access errors if needed.
- S3 access logs (optional) to debug missing files/404s.

## Deployment checklist

1. Create the S3 bucket and set `S3_BUCKET_NAME` env var in Lambdas.
2. Deploy Lambdas (orchestrator + processor). For processor, ensure its role has S3 read/write and the orchestrator role has `lambda:InvokeFunction` on the processor.
3. Set AI-related env vars (`BEDROCK_MODEL_ID`) and ensure the Bedrock execution role/permissions are configured. For example, set `BEDROCK_MODEL_ID=meta us.meta.llama3-1-70b-instruct-v1:0`.
4. Configure Amplify app and point it to the frontend repository/branch; confirm build settings (Vite build command and publish dir `dist`).
5. Add CloudWatch alarms and dashboards for Lambda metrics.

## Troubleshooting tips
- If analytics appear as zero/empty in a cached session: verify that the Processor Lambda fetched match IDs and match details. Check CloudWatch logs for the Processor for lines like `No matches in raw_data - fetching match history` and `Enriched raw_data uploaded back to S3`.
- If Processor is not running: check Orchestrator CloudWatch logs for `Failed to invoke processor Lambda` and confirm `PROCESSOR_LAMBDA_NAME` env var and orchestrator IAM permissions.
- For AI failures: inspect Processor logs for errors produced by `InsightsGenerator`/`HumorGenerator` and validate model endpoint health and permissions.

## Recommendations & improvements

- Add granular CloudWatch metrics (duration, success/failure counts) for each logical step (fetch, analytics, humor generation) to speed troubleshooting.
- Consider runtime feature flags and graceful degradation: if Bedrock is unavailable, return analytics-only responses and record that AI generation was skipped.
- Implement request rate-limiting and client-side backoff to avoid excessive invocations and API throttling.
