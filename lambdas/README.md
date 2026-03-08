# Autonomous Pricing Engine - AWS Lambda Functions

Production-ready AWS serverless implementation for an AI-powered pricing manager targeting small sellers.

## The "AI Pricing Manager" Concept

Your **AI Pricing Manager** works like a smart employee:

| Scenario | What Happens | AI Usage |
|----------|--------------|----------|
| **Routine pricing** | Fast deterministic math | No LLM (instant, free) |
| **Edge cases** | AI analyzes and corrects | LLM called (smart) |
| **Seller asks "Why?"** | Natural language explanation | LLM called (helpful) |
| **Daily summary** | AI-written report | 1 LLM call per day (efficient) |
| **Onboarding** | Personalized setup | 1 LLM call (welcoming) |

**Result:** AI is *central* but *cost-optimized* - perfect for small sellers.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI Pricing Manager                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐                        ┌──────────────────────┐      │
│   │   SELLER     │◀─────── Natural ──────▶│    AI INTERFACE      │      │
│   │  (Business)  │       Language         │    (LLM Powered)     │      │
│   └──────────────┘                        └──────────┬───────────┘      │
│                                                      │                   │
│                    ┌─────────────────────────────────┘                   │
│                    │                                                     │
│   ┌────────────────▼────────────────┐                                   │
│   │         FAST PATH               │    ← 90% of decisions             │
│   │    (Deterministic Logic)        │      Instant, no LLM              │
│   │                                 │                                   │
│   │  ┌─────────┐  ┌─────────┐      │                                   │
│   │  │ Market  │─▶│ Pricing │       │                                   │
│   │  │Processor│  │ Engine  │       │                                   │
│   │  └─────────┘  └────┬────┘       │                                   │
│   │                    │            │                                   │
│   │              ┌─────▼─────┐      │                                   │
│   │              │ Guardrail │      │                                   │
│   │              │ Executor  │      │                                   │
│   │              └─────┬─────┘      │                                   │
│   └────────────────────│────────────┘                                   │
│                        │                                                 │
│   ┌────────────────────▼────────────┐                                   │
│   │         AI LAYER                │    ← 10% when needed              │
│   │    (LLM Intelligence)           │      Smart corrections            │
│   │                                 │                                   │
│   │  ┌───────────┐  ┌────────────┐ │                                   │
│   │  │Monitoring │─▶│ Correction │   │                                   │
│   │  │  Agent    │  │   Agent    │   │                                   │
│   │  └───────────┘  └────────────┘ │                                   │
│   └─────────────────────────────────┘                                   │
│                                                                          │
│   ┌─────────────────────────────────┐                                   │
│   │         DATA LAYER              │                                   │
│   │  ┌──────────┐ ┌──────────┐     │                                   │
│   │  │ Products │ │Decisions │      │                                   │
│   │  └──────────┘ └──────────┘     │                                   │
│   │  ┌──────────┐                  │                                   │
│   │  │Corrections│                 │                                   │
│   │  └──────────┘                  │                                   │
│   └─────────────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
lambdas/
├── shared/
│   ├── __init__.py          # Module exports
│   ├── constants.py         # Environment constants
│   ├── dynamodb.py          # DynamoDB client wrapper
│   └── utils.py             # Utility functions
├── market_processor/
│   ├── handler.py           # Market data ingestion
│   └── requirements.txt
├── pricing_engine/
│   ├── handler.py           # Deterministic pricing logic
│   └── requirements.txt
├── guardrail_executor/
│   ├── handler.py           # Business rule validation
│   └── requirements.txt
├── monitoring_agent/
│   ├── handler.py           # Performance monitoring
│   └── requirements.txt
├── correction_agent/
│   ├── handler.py           # AI-powered corrections
│   └── requirements.txt
├── ai_interface/            # ⭐ NEW - The "face" of AI
│   ├── handler.py           # Natural language, summaries, onboarding
│   └── requirements.txt
├── events/                  # Sample event JSONs
├── template.yaml            # SAM deployment template
├── env_config.json          # Environment variables
└── README.md
```

---

## Lambda Functions

### 1. Market Processor
**Purpose:** Ingest market data (competitor prices, demand signals)

**When AI is used:** Never (deterministic)
**Cost:** ₹0 per call

---

### 2. Pricing Engine
**Purpose:** Calculate recommended prices using deterministic logic

**Pricing Logic:**
```python
cost_with_gst = cost_price × (1 + gst_percent/100)
min_viable_price = cost_with_gst × (1 + min_margin_percent/100)
demand_adjusted = min_viable_price × demand_factor
final_price = optimize(demand_adjusted, competitor_positioned)
```

**When AI is used:** Never (deterministic)
**Cost:** ₹0 per call

---

### 3. Guardrail Executor
**Purpose:** Validate pricing decisions against business rules

**Rules:**
- ✅ Margin floor: Minimum 5% margin
- ✅ Cost protection: Price > cost + GST
- ✅ Drop limit: Max 25% decrease

**When AI is used:** Never (deterministic rules)
**Cost:** ₹0 per call

---

### 4. Monitoring Agent
**Purpose:** Compare predicted vs actual performance

**When AI is used:** Never (threshold check)
**Cost:** ₹0 per call
**Triggers:** Correction agent if deviation > 20%

---

### 5. Correction Agent
**Purpose:** AI-powered price corrections using AWS Bedrock

**When AI is used:** When triggered by monitoring (>20% deviation)
**Cost:** ~₹0.02-0.05 per correction

**Example Output:**
```json
{
  "analysis": "Lower demand than predicted due to competitor promotion",
  "revised_price": 485.00,
  "confidence": "medium",
  "explanation": "Competitor ran a flash sale that captured 15% of market share..."
}
```

---

### 6. AI Interface ⭐ NEW
**Purpose:** The human-facing AI assistant for sellers

**Query Types:**

| Type | Description | AI Usage |
|------|-------------|----------|
| `query` | Natural language questions | 1 LLM call |
| `daily_summary` | AI-written daily report | 1 LLM call/day |
| `onboarding` | Personalized welcome & setup | 1 LLM call |
| `strategy` | Strategic business insights | 1 LLM call |
| `bulk_explanation` | Explain 10 decisions at once | 1 LLM call |

**Example Interactions:**

```
Seller: "Why is my iPhone case priced at ₹299?"

AI: "I set ₹299 because your competitor dropped to ₹320 last week
and demand is slightly low (0.8x). This maintains your 8% margin
while staying competitive. Want me to adjust?"
```

```
Seller: "Give me my daily summary"

AI: "Good morning! 🌟 Yesterday you made ₹12,450 in estimated profit.
I adjusted 3 prices - the iPhone case is now at ₹299 and performing
well. However, your USB charger dropped 15% in sales. Want me to
review the pricing?"
```

---

## Cost Optimization Strategy

| Operation | Frequency | LLM Calls | Cost/Month |
|-----------|-----------|-----------|------------|
| Routine pricing | 1000/day | 0 | ₹0 |
| Corrections | 10/day | 10 | ~₹15 |
| Daily summaries | 1/day | 1 | ~₹1.50 |
| Seller queries | 5/day | 5 | ~₹7.50 |
| Onboarding | 1 time | 1 | ~₹1.50 |
| **Total** | - | **~17/day** | **~₹25/month** |

**Perfect for small sellers who can't afford expensive AI!**

---

## DynamoDB Tables

### Products Table
```json
{
  "product_id": "PROD-001",
  "seller_id": "SELLER-001",
  "product_name": "iPhone 15 Silicone Case",
  "cost_price": 150.00,
  "current_price": 299.00,
  "competitor_price": 349.00,
  "demand_factor": 1.2,
  "gst_percent": 18.0,
  "margin": 12.5
}
```

### Decisions Table
```json
{
  "decision_id": "decision_PROD-001_2025-01-15T10-30-00",
  "product_id": "PROD-001",
  "status": "approved",
  "recommended_price": 299.00,
  "predicted_margin": 12.5,
  "predicted_sales": 115
}
```

### Corrections Table
```json
{
  "correction_id": "correction_PROD-001_2025-01-15T12-00-00",
  "product_id": "PROD-001",
  "ai_analysis": {...},
  "revised_price": 285.00
}
```

---

## API Endpoints

### AI Interface API

```bash
# Natural Language Query
POST /ai/query
{
  "seller_id": "SELLER-001",
  "query": "Why is my iPhone case priced at ₹299?",
  "product_id": "PROD-001"
}

# Daily Summary
POST /ai/daily_summary
{
  "seller_id": "SELLER-001"
}

# Onboarding
POST /ai/onboarding
{
  "seller_id": "SELLER-001",
  "seller_info": {
    "business_name": "Chennai Mobiles",
    "business_type": "Electronics",
    "experience": "Beginner"
  },
  "products": [...]
}

# Strategy Insights
POST /ai/strategy
{
  "seller_id": "SELLER-001",
  "timeframe": "week"
}
```

---

## Deployment

```bash
# Build
sam build

# Deploy with guided setup
sam deploy --guided

# Test locally
sam local invoke AIInterfaceFunction -e events/ai_interface_query_event.json
```

---

## Event Flow Example

```
1. Market data arrives → market_processor
   └─ Updates product with competitor_price: ₹599

2. Pricing triggered → pricing_engine
   └─ Calculates: recommended_price: ₹465, margin: 10.5%

3. Validation → guardrail_executor
   └─ Checks: ✅ margin OK, ✅ above cost, ✅ < 25% drop
   └─ Applies price to product

4. Sales period ends → monitoring_agent
   └─ Compares: predicted 115 vs actual 85 (26% deviation)
   └─ Triggers correction

5. AI Correction → correction_agent
   └─ Calls Bedrock: "Analyze deviation..."
   └─ Returns: revised_price: ₹485, explanation

6. Seller asks → ai_interface
   └─ "Why did you change the price?"
   └─ Calls Bedrock: Natural language explanation
```

---
