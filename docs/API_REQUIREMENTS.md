# API Gateway Requirements for Frontend

## Overview
The Next.js frontend requires the following REST API endpoints from AWS API Gateway. All endpoints should return JSON and support CORS.

---

## 📊 Dashboard APIs

### GET /dashboard/kpis
**Purpose:** Fetch key performance indicators for dashboard overview

**Response:**
```json
{
  "activeProducts": 125,
  "avgMargin": 23.5,
  "revenueToday": 45000,
  "aiConfidence": 87.3,
  "activeProductsDelta": 5,
  "avgMarginDelta": 1.2,
  "revenueDelta": 8.5,
  "confidenceDelta": 2.1
}
```

---

## 📦 Product APIs

### GET /products
**Purpose:** List all products with current pricing

**Response:**
```json
[
  {
    "id": "PROD-001",
    "name": "Wireless Bluetooth Earbuds",
    "cost": 450,
    "currentPrice": 899,
    "competitorPrice": 849,
    "margin": 23.5,
    "status": "stable",
    "category": "Electronics",
    "lastUpdated": "2025-01-15T10:30:00Z",
    "sku": "WBE-001",
    "inventoryLevel": 150,
    "demandScore": 1.2
  }
]
```

### GET /products/:id
**Purpose:** Get detailed product information with history and decisions

**Response:**
```json
{
  "id": "PROD-001",
  "name": "Wireless Bluetooth Earbuds",
  "cost": 450,
  "currentPrice": 899,
  "competitorPrice": 849,
  "margin": 23.5,
  "status": "adjusted",
  "category": "Electronics",
  "lastUpdated": "2025-01-15T10:30:00Z",
  "historicalPrices": [
    {
      "date": "2025-01-15",
      "price": 899,
      "competitorPrice": 849
    }
  ],
  "decisions": [
    {
      "id": "DEC-001",
      "productId": "PROD-001",
      "productName": "Wireless Bluetooth Earbuds",
      "oldPrice": 999,
      "newPrice": 899,
      "reason": "Competitor price drop detected",
      "confidence": 0.92,
      "type": "ai_correction",
      "timestamp": "2025-01-15T10:30:00Z",
      "status": "applied"
    }
  ]
}
```

### GET /products/:id/history
**Purpose:** Get historical pricing data for charts

**Response:**
```json
[
  {
    "date": "2025-01-01",
    "price": 999,
    "competitorPrice": 950
  },
  {
    "date": "2025-01-15",
    "price": 899,
    "competitorPrice": 849
  }
]
```

---

## 🎯 Pricing Decision APIs

### GET /decisions/recent
**Purpose:** Get recent pricing decisions for dashboard

**Response:**
```json
[
  {
    "id": "DEC-001",
    "productId": "PROD-001",
    "productName": "Wireless Bluetooth Earbuds",
    "oldPrice": 999,
    "newPrice": 899,
    "reason": "Competitor price drop detected",
    "confidence": 0.92,
    "type": "ai_correction",
    "timestamp": "2025-01-15T10:30:00Z",
    "status": "applied",
    "executionArn": "arn:aws:states:...",
    "stepFunctionRunId": "abc-123"
  }
]
```

### GET /decisions/log
**Purpose:** Get full decision log with all pipeline events

**Response:**
```json
[
  {
    "id": "LOG-001",
    "type": "ai_correction",
    "productName": "Wireless Bluetooth Earbuds",
    "description": "AI recommended price adjustment",
    "timestamp": "2025-01-15T10:30:00Z",
    "status": "success",
    "payload": {
      "oldPrice": 999,
      "newPrice": 899,
      "confidence": 0.92
    }
  }
]
```

---

## 🚨 Alerts API

### GET /alerts
**Purpose:** Get active alerts and warnings

**Response:**
```json
[
  {
    "id": "ALERT-001",
    "type": "warning",
    "message": "Margin below 15% threshold",
    "productName": "USB-C Cable",
    "timestamp": "2025-01-15T10:30:00Z",
    "acknowledged": false
  }
]
```

---

## 📈 Analytics APIs

### GET /analytics/revenue
**Purpose:** Get revenue trend data for charts

**Response:**
```json
[
  {
    "date": "2025-01-01",
    "revenue": 42000,
    "competitor": 38000
  },
  {
    "date": "2025-01-15",
    "revenue": 45000,
    "competitor": 41000
  }
]
```

---

## 🤖 AI Chat API

### POST /ai/query
**Purpose:** Query the AI pricing manager

**Request:**
```json
{
  "query": "Why did my price change for PROD-001?",
  "conversationId": "conv-123",
  "context": {
    "productIds": ["PROD-001"],
    "timeRange": "7d"
  }
}
```

**Response:**
```json
{
  "response": "Your price was adjusted from ₹999 to ₹899 because...",
  "confidence": 0.92,
  "recommendation": "Maintain current price for 48 hours",
  "blocked": false,
  "conversationId": "conv-123",
  "sources": ["pricing_decision_log", "market_data"]
}
```

---

## 🎮 Simulation APIs

### POST /simulate
**Purpose:** Trigger a pricing pipeline simulation

**Request:**
```json
{
  "scenario": "competitor_drop",
  "productIds": ["PROD-001", "PROD-002"]
}
```

**Response:**
```json
{
  "runId": "sim-abc-123",
  "executionArn": "arn:aws:states:us-east-1:123456789012:execution:...",
  "status": "RUNNING"
}
```

### GET /simulate/:runId/status
**Purpose:** Poll simulation progress

**Response:**
```json
{
  "runId": "sim-abc-123",
  "status": "RUNNING",
  "steps": [
    {
      "id": "simulate_event",
      "name": "Generate Market Event",
      "status": "completed",
      "duration": 450
    },
    {
      "id": "market_processor",
      "name": "Process Market Data",
      "status": "running"
    },
    {
      "id": "pricing_engine",
      "name": "Calculate Price",
      "status": "pending"
    }
  ],
  "result": {
    "decisionsApplied": 2,
    "decisionsBlocked": 0,
    "avgConfidence": 0.89
  }
}
```

---

## 🌱 Data Management APIs

### POST /seed
**Purpose:** Seed demo products into database

**Request:**
```json
{
  "productCount": 5,
  "category": "Electronics"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully seeded 5 products",
  "productsSeeded": 5
}
```

### POST /ingest/market-data
**Purpose:** Manually ingest market data

**Request:**
```json
{
  "productId": "PROD-001",
  "competitorPrice": 849,
  "demandScore": 1.2,
  "source": "manual"
}
```

**Response:**
```json
{
  "success": true,
  "productId": "PROD-001",
  "priceUpdated": true
}
```

---

## 🔐 Authentication & Headers

All requests should include:
```
Content-Type: application/json
x-api-key: <API_KEY> (if using API Gateway key)
```

---

## 📝 Summary

**Total Endpoints Required: 14**

| Category | Endpoints | Priority |
|----------|-----------|----------|
| Dashboard | 1 | High |
| Products | 3 | High |
| Decisions | 2 | High |
| Alerts | 1 | Medium |
| Analytics | 1 | Medium |
| AI Chat | 1 | High |
| Simulation | 2 | High |
| Data Management | 2 | Low |

**Critical Path (MVP):**
1. GET /products
2. GET /dashboard/kpis
3. POST /simulate
4. GET /simulate/:runId/status
5. POST /ai/query
6. GET /decisions/recent

**Environment Variables:**
```env
API_BASE=https://your-api-id.execute-api.region.amazonaws.com/prod
API_GATEWAY_KEY=your-api-key (optional)
```
