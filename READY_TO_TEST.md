# ✅ API Connected - Final Steps

## What I Did
✅ Updated `frontend/.env.local` with your deployed API URL:
```
API_BASE=https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com
```

## What You Need to Do Now

### Step 1: Test Backend
```bash
test-backend.bat
```

This will:
- Seed 5 demo products
- Verify products endpoint works
- Verify dashboard endpoint works

### Step 2: Restart Frontend
```bash
cd frontend

# Stop the dev server (Ctrl+C)
# Then restart:
pnpm dev
```

### Step 3: Verify Integration
1. Open http://localhost:3000/dashboard
2. Open browser DevTools (F12) → Network tab
3. Refresh page
4. Look for API calls to `nz9mt0diz3.execute-api.us-east-1.amazonaws.com`
5. Should see real data (not mock)

## Expected Results

### Dashboard Should Show:
- ✅ 5 products (from seed)
- ✅ Real KPIs (calculated from DynamoDB)
- ✅ Empty decisions (run simulation to populate)
- ✅ Alerts (if any low margins)

### Test Simulation:
1. Go to /simulation page
2. Click "Run Simulation"
3. Select scenario (e.g., "Competitor Price Drop")
4. Watch Step Functions pipeline execute
5. Check /decisions page for results

### Test AI Chat:
1. Go to /ai-chat page
2. Ask: "Why did my price change?"
3. Should get real AI response from Bedrock

## Quick Verification Commands

```bash
# Test all endpoints
curl https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com/products
curl https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com/dashboard/kpis
curl https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com/decisions/recent
curl https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com/alerts
curl https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com/analytics/revenue

# Run simulation
curl -X POST https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"competitor_drop"}'

# Ask AI
curl -X POST https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query_type":"query","seller_id":"SELLER-001","query":"Why did my price change?"}'
```

## Troubleshooting

### Still seeing mock data?
1. Check `.env.local` has correct URL
2. Restart dev server (Ctrl+C, then `pnpm dev`)
3. Hard refresh browser (Ctrl+Shift+R)
4. Check browser console for errors

### Backend returns empty arrays?
Run seed: `curl -X POST https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com/seed`

### 500 errors?
Check Lambda logs:
```bash
aws logs tail /aws/lambda/autonomous-pricing-query-api --follow
```

## Demo Checklist

- [ ] Backend deployed ✅ (Done)
- [ ] Frontend .env.local updated ✅ (Done)
- [ ] Backend seeded with products (Run `test-backend.bat`)
- [ ] Frontend restarted (Ctrl+C, then `pnpm dev`)
- [ ] Dashboard shows real data
- [ ] Simulation works
- [ ] AI chat responds
- [ ] All pages load without errors

## Your API Endpoints

Base URL: `https://nz9mt0diz3.execute-api.us-east-1.amazonaws.com`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /products | GET | List products |
| /products/{id} | GET | Product detail |
| /dashboard/kpis | GET | Dashboard metrics |
| /decisions/recent | GET | Recent decisions |
| /decisions/log | GET | Decision log |
| /alerts | GET | Active alerts |
| /analytics/revenue | GET | Revenue trends |
| /simulate | POST | Run simulation |
| /ai/query | POST | AI chat |
| /seed | POST | Seed demo data |

**Status**: 🎯 Ready for demo!

**Next**: Run `test-backend.bat` then restart frontend
