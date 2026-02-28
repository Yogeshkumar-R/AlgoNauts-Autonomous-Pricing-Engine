# Autonomous Pricing Engine - AWS Architecture

## Architecture Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        AUTONOMOUS PRICING ENGINE - AWS ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────────┐
                                    │   EXTERNAL       │
                                    │   DATA SOURCES   │
                                    │                  │
                                    │ • Competitor    │
                                    │   Prices        │
                                    │ • Demand Signals │
                                    │ • Market Trends  │
                                    └────────┬─────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              INGESTION LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│    ┌──────────────────┐         ┌──────────────────┐                               │
│    │   Amazon SQS     │         │  Amazon          │                               │
│    │   Market Data    │────────▶│  EventBridge     │                               │
│    │   Queue          │         │  Event Bus       │                               │
│    └──────────────────┘         └────────┬─────────┘                               │
│                                          │                                          │
└──────────────────────────────────────────┼──────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           PRICING DECISION ENGINE                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                     AWS LAMBDA FUNCTIONS                                     │   │
│   │                                                                              │   │
│   │  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐                 │   │
│   │  │    MARKET     │   │   PRICING     │   │  GUARDRAIL    │                 │   │
│   │  │   PROCESSOR   │──▶│    ENGINE     │──▶│   EXECUTOR    │                 │   │
│   │  │               │   │               │   │               │                 │   │
│   │  │ • Parse data  │   │ • Calculate   │   │ • Validate    │                 │   │
│   │  │ • Update      │   │   optimal     │   │   margin      │                 │   │
│   │  │   products    │   │   price       │   │ • Check       │                 │   │
│   │  │               │   │ • Predict     │   │   safety      │                 │   │
│   │  │               │   │   sales       │   │   rules       │                 │   │
│   │  └───────────────┘   └───────────────┘   └───────┬───────┘                 │   │
│   │                                                   │                          │   │
│   │                                                   ▼                          │   │
│   │                            ┌───────────────────────────────┐                │   │
│   │                            │         APPROVED              │                │   │
│   │                            │         DECISION              │                │   │
│   │                            └───────────────────────────────┘                │   │
│   │                                       │                                     │   │
│   └───────────────────────────────────────┼─────────────────────────────────────┘   │
│                                           │                                          │
└───────────────────────────────────────────┼──────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           MONITORING & CORRECTION                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌───────────────────┐         ┌───────────────────────────────┐                  │
│   │   MONITORING      │         │      CORRECTION               │                  │
│   │   AGENT           │────────▶│      AGENT                    │                  │
│   │   (Lambda)        │         │      (Lambda + Bedrock)       │                  │
│   │                   │         │                               │                  │
│   │ • Compare         │         │ • AI Root Cause Analysis      │                  │
│   │   predicted vs    │         │ • Revised recommendations     │                  │
│   │   actual sales    │         │ • Natural language            │                  │
│   │ • Trigger         │         │   explanations                │                  │
│   │   corrections     │         │ • Confidence scoring          │                  │
│   │                   │         │                               │                  │
│   │                   │         │  ┌─────────────────────────┐  │                  │
│   │                   │         │  │   Amazon Bedrock        │  │                  │
│   │                   │         │  │   Claude 3 Sonnet       │  │                  │
│   │                   │         │  │                         │  │                  │
│   │                   │         │  │   • Reasoning           │  │                  │
│   │                   │         │  │   • Analysis            │  │                  │
│   │                   │         │  │   • Explanation         │  │                  │
│   │                   │         │  └─────────────────────────┘  │                  │
│   └───────────────────┘         └───────────────────────────────┘                  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           AI INTERFACE LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌──────────────────┐         ┌───────────────────────────────┐                  │
│   │   Amazon API     │────────▶│    AI INTERFACE               │                  │
│   │   Gateway        │         │    (Lambda + Bedrock)        │                  │
│   │                  │         │                               │                  │
│   │  POST /ai/query  │         │  • Natural language queries   │                  │
│   │  POST /ai/summary│         │  • Daily summaries            │                  │
│   │  POST /ai/insight│         │  • Seller onboarding          │                  │
│   │                  │         │  • Strategy recommendations   │                  │
│   │                  │         │                               │                  │
│   │                  │         │  ┌─────────────────────────┐  │                  │
│   │                  │         │  │   Amazon Bedrock        │  │                  │
│   │                  │         │  │   Claude 4.5 haiku      │  │                  │
│   │                  │         │  └─────────────────────────┘  │                  │
│   └──────────────────┘         └───────────────────────────────┘                  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐        │
│   │    DynamoDB        │  │    DynamoDB        │  │    DynamoDB          │        │
│   │    Products        │  │    Decisions       │  │    Corrections       │        │
│   │    Table           │  │    Table            │  │    Table             │        │
│   │                     │  │                     │  │                      │        │
│   │  • product_id       │  │  • decision_id      │  │  • correction_id     │        │
│   │  • name             │  │  • product_id       │  │  • product_id        │        │
│   │  • cost_price       │  │  • recommended_     │  │  • root_cause        │        │
│   │  • current_price    │  │    price            │  │  • ai_explanation    │        │
│   │  • competitor_price │  │  • predicted_sales  │  │  • correction_time   │        │
│   │  • demand_factor    │  │  • actual_sales     │  │  • confidence        │        │
│   │  • margin           │  │  • strategy         │  │                      │        │
│   │                     │  │  • timestamp        │  │                      │        │
│   └─────────────────────┘  └─────────────────────┘  └─────────────────────┘        │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────┐  │
│   │                        STREAMLIT DASHBOARD                                   │  │
│   │                                                                              │  │
│   │   ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐   │  │
│   │   │  Product Management │  │  Pricing Decisions  │  │  AI Insights     │   │  │
│   │   │                     │  │                     │  │                  │   │  │
│   │   │  • View products    │  │  • View decisions   │  │  • Ask questions │   │  │
│   │   │  • Update prices    │  │  • Approve/Reject   │  │  • Get summaries  │   │  │
│   │   │  • Track margin     │  │  • View reasoning   │  │  • Get strategy  │   │  │
│   │   └─────────────────────┘  └─────────────────────┘  └──────────────────┘   │  │
│   │                                                                              │  │
│   │   ┌─────────────────────────────────────────────────────────────────────┐   │  │
│   │   │                    BEDROCK REASONING DISPLAY                        │   │  │
│   │   │                                                                      │   │  │
│   │   │   "The price was adjusted from ₹299 to ₹259 because competitor      │   │  │
│   │   │    dropped prices by 15%. Based on demand elasticity analysis,      │   │  │
│   │   │    this 13% reduction should increase sales volume by 22% while     │   │  │
│   │   │    maintaining 8% margin. Confidence: 87%"                          │   │  │
│   │   │                                                                      │   │  │
│   │   └─────────────────────────────────────────────────────────────────────┘   │  │
│   │                                                                              │  │
│   └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────┐  │
│   │                    HOSTING: AWS Amplify / EC2                               │  │
│   └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## AI Integration Flow (Why AI is Required)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    WHY AI IS REQUIRED - AUTONOMY LOOP                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────┐                                                            │
   │  COMPETITOR     │                                                            │
   │  PRICE DROP     │                                                            │
   │  (Event)        │                                                            │
   └────────┬────────┘                                                            │
            │                                                                     │
            ▼                                                                     │
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
   │  TRADITIONAL     │    │  RULE-BASED     │    │  ❌ PROBLEM     │            │
   │  APPROACH        │───▶│  PRICING        │───▶│                 │            │
   │                  │    │                 │    │  • No reasoning │            │
   │                  │    │  • Fixed rules  │    │  • No adaptive │            │
   │                  │    │  • No context   │    │    correction  │            │
   │                  │    │                 │    │  • No trust    │            │
   └─────────────────┘    └─────────────────┘    └─────────────────┘            │
                                                                                 │
   ┌─────────────────────────────────────────────────────────────────────────────┐ │
   │                     AI-POWERED APPROACH (BEDROCK)                           │ │
   │                                                                             │ │
   │  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐              │ │
   │  │  DETECT       │    │  ANALYZE      │    │  REASON       │              │ │
   │  │  Event        │───▶│  Context       │───▶│  (Bedrock)    │              │ │
   │  │               │    │               │    │               │              │ │
   │  │  Price drop   │    │  Market cond. │    │  • Why?       │              │ │
   │  │  detected     │    │  Demand       │    │  • Impact?    │              │ │
   │  │               │    │  Competition  │    │  • Confidence?│              │ │
   │  └───────────────┘    └───────────────┘    └───────┬───────┘              │ │
   │                                                    │                       │ │
   │                                                    ▼                       │ │
   │  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐              │ │
   │  │  EXPLAIN      │◀───│  CORRECT      │◀───│  DECIDE       │              │ │
   │  │  (Natural     │    │  (If needed)  │    │  New price    │              │ │
   │  │   Language)   │    │               │    │               │              │ │
   │  │               │    │  AI notices   │    │               │              │ │
   │  │  "Competitor  │    │  deviation,   │    │               │              │ │
   │  │   dropped by  │    │  analyzes     │    │               │              │ │
   │  │   15%, so we  │    │  root cause,  │    │               │              │ │
   │  │   adjusted..." │    │  corrects"    │    │               │              │ │
   │  └───────────────┘    └───────────────┘    └───────────────┘              │ │
   │                                                                             │ │
   └─────────────────────────────────────────────────────────────────────────────┘ │

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      VALUE AI ADDS TO USER EXPERIENCE                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                     WITHOUT AI                        WITH AI              │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   ❌ No explanation           ───────────────▶  ✅ Clear reasoning         │   │
│   │                                                                             │   │
│   │   ❌ No adaptive correction   ───────────────▶  ✅ Self-correcting loop     │   │
│   │                                                                             │   │
│   │   ❌ Manual monitoring        ───────────────▶  ✅ Autonomous monitoring    │   │
│   │                                                                             │   │
│   │   ❌ No trust (black box)     ───────────────▶  ✅ Transparent decisions    │   │
│   │                                                                             │   │
│   │   ❌ Calculator approach      ───────────────▶  ✅ Pricing Manager approach │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## AWS Services Used

| Category | Service | Purpose |
|----------|---------|---------|
| **Generative AI** | Amazon Bedrock (Claude 3 Sonnet) | Reasoning, analysis, explanations |
| **Compute** | AWS Lambda | Serverless function execution |
| **Database** | Amazon DynamoDB | Product, decision, correction data |
| **API** | Amazon API Gateway | REST API for AI interface |
| **Events** | Amazon EventBridge | Event-driven orchestration |
| **Queue** | Amazon SQS | Market data buffering |
| **Logging** | Amazon CloudWatch | Monitoring and logs |

---

## Why This Architecture Wins Technical Points

1. **✅ Bedrock Integration**: Core to decision-making, not cosmetic
2. **✅ Serverless Pattern**: Lambda + DynamoDB + EventBridge
3. **✅ Event-Driven**: Loose coupling, scalable
4. **✅ AI Explanation Layer**: Bedrock reasoning exposed to users
5. **✅ Autonomous Loop**: Monitor → Correct → Explain