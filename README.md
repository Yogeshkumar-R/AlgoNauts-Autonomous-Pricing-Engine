# AlgoNauts: Autonomous Pricing Engine

Autonomous pricing assistant for Indian SMEs, built on AWS serverless.

## What It Does
- Shows product-level profit and margin insights
- Compares your price with market signals
- Recommends pricing actions: `KEEP`, `LOWER`, `RAISE`
- Explains each recommendation with confidence
- Supports simulation runs before applying strategy
- Provides AI chat for pricing queries and reasoning

## Current Architecture
- Frontend: Next.js app deployed on AWS Amplify
- BFF Layer: Next.js route handlers under `frontend/app/api/*`
- Backend API: API Gateway (HTTP API) + Lambda
- Orchestration: Step Functions pricing pipeline
- Data: DynamoDB (products, decisions, corrections, chat history)
- Eventing: EventBridge
- AI: Amazon Bedrock
- Observability: CloudWatch, LangSmith

Architecture reference:
- `.kiro/specs/autonomous-pricing-engine/architecture/aws-prototype-architecture.md`
- `.kiro/specs/autonomous-pricing-engine/architecture/aws-architecture-amplify-serverless.md`

## Repository Structure
```text
.
|-- .kiro/specs/               # Product/design/requirements specs
|-- frontend/                  # Next.js UI + /api proxy routes
|-- lambdas/                   # Lambda functions + SAM template
|-- infrastructure/            # Infra helper files
`-- README.md
```

## Frontend API Surface (via `/api/*`)
- `GET /api/dashboard/kpis`
- `GET /api/products`
- `GET /api/products/:productId`
- `GET /api/products/:productId/history`
- `GET /api/decisions/recent`
- `GET /api/decisions/log`
- `GET /api/alerts`
- `GET /api/analytics/revenue`
- `GET /api/ai/conversations`
- `POST /api/ai/query`
- `POST /api/simulate`
- `GET /api/simulate/:runId/status`
- `POST /api/seed`
- `POST /api/ingest/market-data`

## Local Development
### 1. Frontend
```bash
cd frontend
npm install
npm run dev
```

Set environment variables in `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://<api-id>.execute-api.<region>.amazonaws.com
```

If `NEXT_PUBLIC_API_URL` is not set, supported routes use mock fallback behavior.

### 2. Backend (SAM)
```bash
cd lambdas
sam build
sam deploy --guided
```

## Deployment
### Frontend (Amplify)
1. Connect repository/branch in AWS Amplify.
2. Configure `NEXT_PUBLIC_API_URL`.
3. Deploy.

### Backend (API Gateway + Lambda)
1. Deploy `lambdas/template.yaml` using SAM.
2. Use stack outputs for API URL and resource ARNs.
3. Ensure CORS allowlist includes Amplify domain.

## Product Goals
- Keep seller UX simple and action-oriented
- Achieve fast decision-to-execution loops
- Maintain explainability and confidence visibility
- Keep infrastructure cost-efficient with serverless primitives

## License
MIT
