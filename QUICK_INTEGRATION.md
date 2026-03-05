# Quick API Integration Guide

## Current Status
✅ Frontend API routes are ready
✅ Backend Lambda is ready
❌ Not connected (showing mock data)

## Fix in 2 Steps

### Step 1: Deploy Backend (if not done)
```bash
cd lambdas
sam build
sam deploy --guided
```

Copy the API URL from output (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com`)

### Step 2: Update Frontend .env.local
```bash
cd frontend
```

Edit `.env.local` and replace with your actual API URL:
```env
API_BASE=https://abc123.execute-api.us-east-1.amazonaws.com
```

### Step 3: Restart Frontend
```bash
# Stop the dev server (Ctrl+C)
pnpm dev
```

## Verify Connection

Open browser console and check:
```javascript
// Should see real API calls, not mock data
fetch('/api/products').then(r => r.json()).then(console.log)
```

## Test Backend Directly

```bash
# Replace with your actual API URL
curl https://abc123.execute-api.us-east-1.amazonaws.com/products
```

Should return empty array `[]` (no products yet)

Then seed:
```bash
curl -X POST https://abc123.execute-api.us-east-1.amazonaws.com/seed
```

Now products endpoint should return data.

## All API Mappings

| Frontend Route | Backend Endpoint | Status |
|---------------|------------------|--------|
| GET /api/products | GET /products | ✅ Ready |
| GET /api/products/[id] | GET /products/{id} | ✅ Ready |
| GET /api/dashboard/kpis | GET /dashboard/kpis | ✅ Ready |
| GET /api/decisions/recent | GET /decisions/recent | ✅ Ready |
| GET /api/decisions/log | GET /decisions/log | ⚠️ Not implemented in backend |
| GET /api/alerts | GET /alerts | ✅ Ready |
| GET /api/analytics/revenue | GET /analytics/revenue | ✅ Ready |
| POST /api/simulate | POST /simulate | ✅ Ready |
| POST /api/ai/query | POST /ai/query | ✅ Ready |
| POST /api/seed | POST /seed | ✅ Ready |

## Missing Backend Endpoint

`GET /decisions/log` is not implemented in backend. Options:

1. **Use /decisions/recent instead** (already works)
2. **Add to query_api Lambda**:

```python
# In query_api/handler.py, add:
elif path == '/decisions/log':
    response = get_recent_decisions()  # Same as recent for now
```

## Quick Test Script

```bash
# Set your API URL
export API_BASE="https://YOUR-API.execute-api.us-east-1.amazonaws.com"

# Test all endpoints
echo "Testing /seed..."
curl -X POST $API_BASE/seed

echo "\nTesting /products..."
curl $API_BASE/products

echo "\nTesting /dashboard/kpis..."
curl $API_BASE/dashboard/kpis

echo "\nTesting /decisions/recent..."
curl $API_BASE/decisions/recent

echo "\nTesting /alerts..."
curl $API_BASE/alerts

echo "\nTesting /analytics/revenue..."
curl $API_BASE/analytics/revenue

echo "\nTesting /simulate..."
curl -X POST $API_BASE/simulate -H "Content-Type: application/json" -d '{"scenario":"competitor_drop"}'

echo "\nAll tests complete!"
```

## Troubleshooting

### Still seeing mock data?
1. Check `.env.local` exists and has correct URL
2. Restart dev server
3. Clear browser cache
4. Check browser console for errors

### Backend returns empty data?
Run seed first: `curl -X POST $API_BASE/seed`

### CORS errors?
Already handled in Lambda - check API Gateway CORS settings

### 404 errors?
Verify Lambda is deployed: `aws lambda list-functions | grep pricing`
