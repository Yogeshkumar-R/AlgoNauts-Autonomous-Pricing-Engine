# Connecting Backend APIs to Frontend - Quick Guide

## Step 1: Deploy Backend (Get API URL)

```bash
cd lambdas
sam build
sam deploy --guided
```

**Copy the API Gateway URL from output:**
```
Outputs:
PricingAPIEndpoint = https://abc123xyz.execute-api.us-east-1.amazonaws.com
```

---

## Step 2: Configure Frontend Environment

Create `.env.local` in frontend directory:

```bash
cd ../frontend
```

Create file `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://abc123xyz.execute-api.us-east-1.amazonaws.com
API_GATEWAY_URL=https://abc123xyz.execute-api.us-east-1.amazonaws.com
```

---

## Step 3: Update Frontend API Routes

The frontend already has API routes in `frontend/app/api/*` that need to proxy to your backend.

Update `frontend/lib/backend.ts`:

```typescript
const BACKEND_URL = process.env.API_GATEWAY_URL || process.env.NEXT_PUBLIC_API_URL || ""
```

This file already exists and should work automatically once you set the env variable.

---

## Step 4: Test Connection

```bash
# In frontend directory
npm install  # or pnpm install
npm run dev
```

Open browser: http://localhost:3000

---

## Step 5: Seed Data (First Time Only)

Before using the dashboard, seed demo products:

**Option A - Via Frontend:**
- Go to http://localhost:3000/dashboard
- Look for "Seed Data" button (if available)

**Option B - Via API:**
```bash
curl -X POST https://YOUR-API-URL.amazonaws.com/seed
```

**Option C - Via Browser Console:**
```javascript
fetch('https://YOUR-API-URL.amazonaws.com/seed', {method: 'POST'})
  .then(r => r.json())
  .then(console.log)
```

---

## Step 6: Verify APIs Work

Test each endpoint:

```bash
export API_URL="https://YOUR-API-URL.amazonaws.com"

# 1. Get products
curl $API_URL/products

# 2. Get dashboard KPIs
curl $API_URL/dashboard/kpis

# 3. Get decisions
curl $API_URL/decisions/recent

# 4. Get alerts
curl $API_URL/alerts

# 5. Get analytics
curl $API_URL/analytics/revenue
```

---

## Troubleshooting

### Issue: "BACKEND_NOT_CONFIGURED" error

**Fix:** Make sure `.env.local` exists with correct API URL

```bash
# Check if file exists
cat frontend/.env.local

# Should show:
# NEXT_PUBLIC_API_URL=https://...
```

### Issue: CORS errors in browser

**Fix:** Already handled in Lambda (Access-Control-Allow-Origin: *)

If still seeing errors, check API Gateway CORS settings:
```yaml
# In template.yaml (already configured)
CorsConfiguration:
  AllowOrigins: ["*"]
  AllowMethods: [GET, POST, OPTIONS]
  AllowHeaders: [Content-Type]
```

### Issue: 404 Not Found

**Fix:** Verify API Gateway routes are deployed:

```bash
# List all routes
aws apigatewayv2 get-routes --api-id YOUR_API_ID

# Should see:
# GET /products
# GET /products/{id}
# GET /dashboard/kpis
# etc.
```

### Issue: Empty data in frontend

**Fix:** Seed products first (see Step 5)

---

## Quick Start (All Steps)

```bash
# 1. Deploy backend
cd lambdas
sam build && sam deploy

# 2. Copy API URL from output
# Example: https://abc123.execute-api.us-east-1.amazonaws.com

# 3. Configure frontend
cd ../frontend
echo "NEXT_PUBLIC_API_URL=https://abc123.execute-api.us-east-1.amazonaws.com" > .env.local

# 4. Install & run
pnpm install
pnpm dev

# 5. Seed data (in another terminal)
curl -X POST https://abc123.execute-api.us-east-1.amazonaws.com/seed

# 6. Open browser
# http://localhost:3000
```

---

## Architecture Flow

```
Browser (localhost:3000)
    ↓
Next.js Frontend
    ↓
/app/api/* routes (proxy layer)
    ↓
AWS API Gateway (https://xxx.amazonaws.com)
    ↓
Lambda Functions
    ↓
DynamoDB Tables
```

**Why proxy layer?**
- Hides backend URL from client
- Adds authentication/rate limiting later
- Handles mock data when backend unavailable

---

## Environment Variables Summary

### Backend (Lambda)
Set via SAM template - already configured:
- `PRODUCTS_TABLE`
- `DECISIONS_TABLE`
- `CORRECTIONS_TABLE`
- `BEDROCK_MODEL_ID`
- `LANGSMITH_API_KEY`

### Frontend (Next.js)
Set in `.env.local`:
- `NEXT_PUBLIC_API_URL` - Your API Gateway URL
- `API_GATEWAY_URL` - Same URL (for server-side)

---

## Demo Flow

1. **Start frontend**: `pnpm dev`
2. **Seed products**: POST /seed
3. **View dashboard**: Navigate to /dashboard
4. **Run simulation**: Click "Simulate" button
5. **See results**: Watch decisions appear
6. **Ask AI**: Use chat interface

---

## Production Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

Set environment variable in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` = your API Gateway URL

### Backend (AWS)
Already deployed via SAM!

---

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /products | GET | List products |
| /products/{id} | GET | Product detail |
| /dashboard/kpis | GET | Dashboard metrics |
| /decisions/recent | GET | Recent decisions |
| /alerts | GET | Active alerts |
| /analytics/revenue | GET | Revenue trends |
| /simulate | POST | Run simulation |
| /ai/query | POST | AI chat |
| /seed | POST | Seed demo data |
| /ingest/market-data | POST | Ingest data |

---

**Status**: ✅ Ready to connect!
