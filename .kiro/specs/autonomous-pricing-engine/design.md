# Design Document: Autonomous Pricing Engine (Amplify + Serverless AWS)

## 1. Purpose
This design defines the production architecture and product flow for the Autonomous Pricing Engine, with:
- Frontend deployed on AWS Amplify Hosting
- Backend deployed as serverless APIs on API Gateway + Lambda
- Async pricing orchestration via Step Functions
- Data persisted in DynamoDB

## 2. Product Goals
- Give sellers clear pricing actions: Keep, Lower, Raise
- Show explainable profit impact and confidence for each recommendation
- Support AI-assisted pricing chat with conversation history
- Keep infrastructure simple, low-cost, and hackathon-friendly while production-capable

## 3. User Experience Flow
### 3.1 Core screens
- Dashboard: KPIs, alerts, recent decisions
- Products: list, product detail, history
- AI Chat: natural language pricing guidance with conversation threads
- Simulation: trigger scenario and watch pipeline progress
- Decision Log: historical decisions and outcomes

### 3.2 Primary interaction flow
1. Seller opens Amplify-hosted app.
2. App calls Next.js API routes (`/api/*`).
3. Next.js API routes proxy to API Gateway when `NEXT_PUBLIC_API_URL` is configured.
4. API Gateway invokes Lambda handlers.
5. Lambdas read/write DynamoDB and optionally invoke Step Functions and Bedrock.
6. Frontend renders updated state and explanations.

## 4. Technical Design
### 4.1 Frontend tier
- Next.js App Router UI hosted on Amplify
- Serverless route handlers under `frontend/app/api/*` as backend proxy layer
- Mock fallback mode when backend URL is not configured

### 4.2 API layer
Frontend BFF endpoints (current flow):
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

### 4.3 Compute tier
Lambda functions grouped by behavior:
- Query/API access: query API handlers
- Pipeline: market processor, pricing engine, guardrail executor, monitoring agent, correction agent
- Simulation and ingestion entrypoints
- AI interface for chat and recommendations

### 4.4 Orchestration
- Step Functions controls multi-step pricing pipeline
- API-triggered simulation starts execution
- Frontend polls run status for progress updates

### 4.5 Data tier
DynamoDB tables:
- products
- decisions
- corrections
- chat history

Storage design principles:
- Partition by product or decision identifiers
- GSI for product+timestamp decision lookup
- Keep append-only decision timeline for auditability

### 4.6 AI tier
- Bedrock model calls in correction and AI interface paths
- Confidence score returned with recommendation
- Guardrails and fallback responses for model failures

### 4.7 Event tier
- EventBridge bus distributes market events and internal triggers
- Scheduled/simulated events can trigger pipeline updates

### 4.8 Observability and operations
- CloudWatch Logs for Lambda + Step Functions
- Structured error responses from BFF routes
- Environment-based config to separate local/mock/dev/prod behavior

## 5. Deployment Design
### 5.1 Amplify frontend deployment
- Amplify connected to repository branch
- Build outputs Next.js application
- Environment variables configured in Amplify for runtime integration

Required frontend env:
- `NEXT_PUBLIC_API_URL` (API Gateway base URL)

Optional env:
- feature flags for mock mode and diagnostics

### 5.2 Backend deployment
- SAM template deploys API Gateway, Lambda, DynamoDB, Step Functions, EventBridge
- Least-privilege IAM for each function
- Per-environment stack naming (`dev`, `staging`, `prod`)

### 5.3 CORS and domain model
- Amplify app domain serves frontend
- API Gateway custom domain optional for cleaner URLs
- CORS allowlist must include Amplify domain(s)

## 6. Security Design
- IAM-scoped access between API Gateway, Lambda, Step Functions, DynamoDB
- Secrets kept in environment management (SSM/Secrets Manager recommended)
- Input validation at route and Lambda boundaries
- CloudWatch logging without leaking sensitive fields

## 7. Non-Functional Targets
- p95 API latency for read endpoints: < 800 ms
- Simulation trigger response: < 2 s
- UI freshness for simulation status polling: 2-3 s interval
- Monthly cost optimized for low-traffic startup profile
- Availability target: 99.9% for public read APIs

## 8. Failure and fallback behavior
- If backend unavailable, UI degrades gracefully with mock data where supported
- AI failures return safe fallback text and do not break dashboard rendering
- Long-running simulation failures are surfaced with terminal status and error summary

## 9. Open implementation notes
- `useSearchParams` usage in app routes must be wrapped with Suspense for production build compatibility
- API contracts should stay centralized in `frontend/lib/types.ts` and mirrored by backend schema tests

## 10. Out of scope
- Multi-tenant billing and account management
- Enterprise RBAC and SSO
- Cross-region active-active failover
