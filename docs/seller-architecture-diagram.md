# Seller-Focused Architecture Diagram

## What Sellers See (The Front Door)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🤖 Price Assistant                                │
│              (What sellers interact with)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📊 Dashboard                                                        │
│     • Profit per product                                             │
│     • Competitor comparison                                          │
│     • Recommendations (Keep/Lower/Raise)                            │
│     • Simple explanations                                            │
│     • Weekly profit tracking                                         │
│                                                                       │
│  💬 AI Chat                                                          │
│     • "Why did my price change?"                                     │
│     • "Am I priced competitively?"                                   │
│     • "Should I lower my price today?"                               │
│     • "What's my profit margin?"                                     │
│                                                                       │
│  ⚡ Quick Actions                                                    │
│     • 1-click price adjustment                                       │
│     • Undo last change (5 min)                                       │
│     • Competitor notifications                                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## What's Behind the Scenes (Hidden from Sellers)

```
┌─────────────────────────────────────────────────────────────────────┐
│              🏗️ Technical Architecture (Hidden)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   Lambda     │    │   Lambda     │    │   Lambda     │          │
│  │  Functions   │    │  Functions   │    │  Functions   │          │
│  │              │    │              │    │              │          │
│  │ • Market     │    │ • Pricing    │    │ • Guardrail  │          │
│  │   Processor  │    │   Engine     │    │   Executor   │          │
│  │              │    │              │    │              │          │
│  │ • Monitoring │    │ • Correction │    │ • AI         │          │
│  │   Agent      │    │   Agent      │    │   Interface  │          │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │
│         │                   │                   │                   │
│         └───────────────────┴───────────────────┘                   │
│                             │                                       │
│                    ┌────────▼────────┐                              │
│                    │  Step Functions │                              │
│                    │   Orchestration │                              │
│                    └────────┬────────┘                              │
│                             │                                       │
│         ┌───────────────────┴───────────────────┐                   │
│         │                                       │                   │
│  ┌──────▼──────┐                         ┌──────▼──────┐           │
│  │ DynamoDB    │                         │ DynamoDB    │           │
│  │ Products    │                         │ Decisions   │           │
│  └─────────────┘                         └─────────────┘           │
│                                                                     │
│  ┌──────────────┐         ┌──────────────┐                         │
│  │ EventBridge  │         │ Amazon     │                         │
│  │ Event Bus    │         │ Bedrock    │                         │
│  │              │         │ (Claude)   │                         │
│  └──────────────┘         └──────────────┘                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Seller Journey (What Happens When a Seller Uses the System)

```
Seller opens dashboard
         │
         ▼
Shows: "Your products, your profit, your recommendations"
         │
         ▼
Seller sees: "Wireless Mouse - Profit: ₹350 (58.3%) - Keep - 85%"
         │
         ▼
Seller clicks "Why?" → Gets simple explanation
         │
         ▼
Seller sees: "Competitor lowered price by ₹50. You're 5% above average."
         │
         ▼
Seller clicks "Lower price" → One click → Price updated
         │
         ▼
Seller sees: "Price updated to ₹920. Expected profit: ₹320 (53.3%)"
         │
         ▼
Seller checks weekly summary: "Profit up 12% vs last week"
```

## Key Differences: Seller View vs Technical View

| Seller Sees | Technical Reality |
|-------------|-------------------|
| "Profit dashboard" | DynamoDB Products table queries |
| "Competitor comparison" | Lambda functions polling market data |
| "Keep/Lower/Raise" | Pricing engine algorithm + guardrail validation |
| "Simple explanation" | Bedrock AI generating natural language |
| "Weekly profit" | Aggregated decision logs from DynamoDB |
| "1-click adjustment" | API Gateway + Lambda + DynamoDB update |
| "Undo last change" | Decision history tracking |
| "Competitor notifications" | EventBridge scheduled events |

## The Magic: What Makes This Valuable for Sellers

1. **Profit Visibility**: Every product shows exactly how much money it makes
2. **Competitive Awareness**: Knows if prices are too high or too low
3. **Actionable Guidance**: Tells sellers exactly what to do (not just data)
4. **Trust Through Transparency**: Explains why recommendations are made
5. **Quick Actions**: Changes happen in one click, not complex workflows
6. **Indian Context**: Understands GST, festivals, regional markets

## Success Metrics (From Seller's Perspective)

- Can check all products in <5 minutes
- Can adjust prices in <1 minute  
- Understands 90%+ of recommendations
- Sees 10%+ profit improvement within 30 days
- Feels confident following AI recommendations

---

**Bottom Line**: Sellers don't care about Lambda functions or EventBridge. They care about making more money. This system hides the complexity and delivers simple, actionable profit guidance.
