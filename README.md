# Rift Rewind

Rift Rewind creates a playful, AI-driven "year in review" experience for League of Legends players. Give it a Riot ID and it builds a short, shareable recap featuring highlights from your ranked season, light-hearted commentary, and concise coaching insights — all presented as a set of visual slides.

What it offers
- A personalized, narrative-style recap of a player's season.
- Short, shareable slides with highlights and a humorous voice.
- Coaching-oriented insights that point out strengths and opportunities to improve.

Who this is for
- Players who want a fun summary of their season.
- Content creators and streamers looking for shareable highlights.

Want to run or extend it?
For deployment steps, architecture details, and developer instructions, see the docs in the `docs/` folder (for example `docs/DEPLOYMENT.md` and `docs/AWS_ARCHITECTURE.md`).

## Requirements

- Python 3.10+ (for backend lambdas and the development Flask server)
- Node.js 18+ / npm or yarn (for the frontend Vite app)
- AWS account (optional) CLI configured to deploy Lambdas, S3, API Gateway, and Amplify

Backend Python dependencies are listed in `backend/requirements.txt`.

## Quick start (development)

These steps get you running locally for development and testing.

1) Backend (API + local dev server)

	 - Create a virtual environment and install requirements:

		 python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r backend/requirements.txt

	 - Copy or create a `.env` file in `backend/` with the environment variables you need (see `docs/DEPLOYMENT.md` for recommended vars such as S3_BUCKET_NAME, PROCESSOR_LAMBDA_NAME, BEDROCK_MODEL_ID, AWS_DEFAULT_REGION).

	 - Run the local Flask development server (serves the API endpoints used by the frontend):

		 cd backend; python server.py

	 The dev server runs on http://localhost:8000 by default and proxies CORS to the frontend origins.

2) Frontend (local)

	 - From the repo root install dependencies and run Vite dev server:

		 cd frontend; npm install; npm run dev

	 - Open the Vite dev URL.

3) Testing the flow locally

	 - Use the frontend to start a session. The local Flask server will emulate the API used in production. Note that certain features (calling Bedrock or invoking the processor Lambda) require AWS credentials and deployed Lambdas — see `docs/DEPLOYMENT.md` for details and a local dev fallback option (`RUN_LOCAL_PROCESSOR`).

## Building & preparing for deployment

- Frontend: build the production bundle and deploy to Amplify (or S3+CloudFront)

	cd frontend; npm run build

	The build is written to `frontend/dist` or `frontend/build` depending on how you host it. See `docs/DEPLOYMENT.md` for Amplify guidance.

- Backend Lambdas: the lambdas live under `backend/lambdas/`. Each handler should be packaged with its dependencies (for example using a deployment virtualenv, pip install -r requirements.txt -t ./package, copy lambda files, zip). See `docs/DEPLOYMENT.md` for an example PowerShell packaging script and IAM role recommendations.

## Environment variables & secrets

Sensitive values (AWS credentials, Bedrock model id, S3 bucket names) must be set as environment variables in your Lambda configurations or in a `.env` when running locally. See `docs/DEPLOYMENT.md` for a recommended list (S3_BUCKET_NAME, PROCESSOR_LAMBDA_NAME, BEDROCK_MODEL_ID, AWS_DEFAULT_REGION, RUN_LOCAL_PROCESSOR).

## Where to go next

- For full deployment steps, packaging scripts, IAM permissions and Bedrock usage, read `docs/DEPLOYMENT.md`.
- For architecture and flow diagrams, read `docs/AWS_ARCHITECTURE.md`.

## License
MIT