# System Flowcharts - Autonomous Pricing Engine

## 1. Complete Decision Lifecycle Flow

```mermaid
flowchart TD
    Start([Market Change Occurs]) --> MS[Market Sensing Agent]
    MS -->|Detects price change >5%| MS1{Data Quality Check}
    MS1 -->|Pass| MS2[Enrich with context]
    MS1 -->|Fail >80% deviation| MS3[Flag for manual review]
    MS2 --> SUP1[Supervisor Agent]
    
    SUP1 -->|Route event| PS[Pricing Strategy Agent]
    PS -->|Load product data| PS1[Analyze competitor position]
    PS1 --> PS2[Compute 3 scenarios:<br/>Aggressive, Balanced, Conservative]
    PS2 --> PS3[Select best scenario]
    PS3 --> PS4[AI generates reasoning<br/>via Bedrock/OpenAI]
    PS4 --> PS5[Calculate confidence score]
    PS5 --> SUP2[Supervisor Agent]
    
    SUP2 -->|Validate| GR{Guardrails Check}
    GR -->|Min margin OK?| GR1{Max discount OK?}
    GR1 -->|Velocity limit OK?| GR2{Confidence >0.5?}
    GR2 -->|All pass| EXEC[Execution Agent]
    GR2 -->|Confidence <0.5| HUMAN1[Escalate to Human]
    GR -->|Fail| HUMAN2[Escalate to Human]
    GR1 -->|Fail| HUMAN2
    
    EXEC -->|Calculate GST| EXEC1[Update storefront DB]
    EXEC1 -->|Atomic transaction| EXEC2[Log decision with reasoning]
    EXEC2 -->|Confirm success| MON[Monitoring Agent]
    
    MON -->|Track 24 hours| MON1{Compare actual vs predicted}
    MON1 -->|Within 20%| SUCCESS([Decision Successful])
    MON1 -->|Deviation >20%| MON2[Detect anomaly]
    MON2 --> CORR[Correction Agent]
    
    CORR -->|AI analyzes root cause| CORR1[Classify: competitor_response,<br/>demand_shift, pricing_error]
    CORR1 --> CORR2[Generate corrective strategy<br/>with AI reasoning]
    CORR2 --> CORR3{Correction attempt count}
    CORR3 -->|<3 attempts| SUP3[Supervisor Agent]
    CORR3 -->|≥3 attempts| HUMAN3[Escalate to Human]
    SUP3 -->|Re-validate| GR
    
    HUMAN1 --> END1([Human Decision])
    HUMAN2 --> END1
    HUMAN3 --> END1
    
    style MS fill:#e1f5ff
    style PS fill:#fff4e1
    style EXEC fill:#e8f5e9
    style MON fill:#f3e5f5
    style CORR fill:#ffe0b2
    style SUP1 fill:#ffebee
    style SUP2 fill:#ffebee
    style SUP3 fill:#ffebee
    style GR fill:#ffcdd2
    style SUCCESS fill:#c8e6c9
    style HUMAN1 fill:#ffccbc
    style HUMAN2 fill:#ffccbc
    style HUMAN3 fill:#ffccbc
```

## 2. Agent Interaction Architecture

```mermaid
flowchart LR
    subgraph External
        COMP[Competitor Prices]
        STORE[Storefront Database]
        SALES[Sales Data]
    end
    
    subgraph "Supervisor Agent (Orchestrator)"
        SUP[Supervisor<br/>- Route events<br/>- Enforce guardrails<br/>- Manage escalations]
    end
    
    subgraph "Decision Agents"
        MS[Market Sensing<br/>- Monitor competitors<br/>- Detect changes<br/>- Classify events]
        PS[Pricing Strategy<br/>- Compute scenarios<br/>- AI reasoning<br/>- Confidence scoring]
        EXEC[Execution<br/>- GST calculation<br/>- Update prices<br/>- Log decisions]
        MON[Monitoring<br/>- Track performance<br/>- Detect anomalies<br/>- Calculate accuracy]
        CORR[Correction<br/>- Root cause analysis<br/>- Generate fix<br/>- Re-submit decision]
    end
    
    subgraph "AI Services"
        LLM[Amazon Bedrock /<br/>OpenAI API<br/>- Reasoning generation<br/>- Root cause analysis]
        ML[ML Models<br/>- Demand prediction<br/>- Confidence scoring]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Products, Decisions,<br/>Sales, Logs)]
        CACHE[(Redis<br/>Current state,<br/>Competitor cache)]
    end
    
    COMP -->|15-min polling| MS
    MS -->|market_change event| SUP
    SUP -->|route| PS
    PS <-->|generate reasoning| LLM
    PS <-->|predict demand| ML
    PS -->|pricing_decision| SUP
    SUP -->|approved| EXEC
    EXEC -->|update| STORE
    EXEC -->|log| DB
    EXEC -->|execution_complete| MON
    SALES -->|track| MON
    MON -->|performance_alert| SUP
    SUP -->|route| CORR
    CORR <-->|analyze| LLM
    CORR -->|correction_required| SUP
    
    DB <-->|read/write| MS
    DB <-->|read/write| PS
    DB <-->|read/write| EXEC
    DB <-->|read/write| MON
    DB <-->|read/write| CORR
    CACHE <-->|cache| MS
    CACHE <-->|cache| PS
    
    style SUP fill:#ffebee
    style MS fill:#e1f5ff
    style PS fill:#fff4e1
    style EXEC fill:#e8f5e9
    style MON fill:#f3e5f5
    style CORR fill:#ffe0b2
    style LLM fill:#f0f4c3
    style ML fill:#f0f4c3
```

## 3. Guardrail Validation Flow

```mermaid
flowchart TD
    START([Pricing Decision]) --> GR1{Minimum Margin Check}
    GR1 -->|margin ≥ 25%| GR2{Maximum Discount Check}
    GR1 -->|margin < 25%| REJECT1[❌ Reject: Margin too low]
    
    GR2 -->|discount ≤ 20%| GR3{Velocity Limit Check}
    GR2 -->|discount > 20%| REJECT2[❌ Reject: Discount too high]
    
    GR3 -->|changes < 3/day| GR4{Price Change Magnitude}
    GR3 -->|changes ≥ 3/day| QUEUE[⏸️ Queue for later]
    
    GR4 -->|change < 30%| GR5{Confidence Score}
    GR4 -->|change ≥ 30%| HUMAN1[👤 Human approval required]
    
    GR5 -->|confidence ≥ 0.8| APPROVE1[✅ Approve: Execute autonomously]
    GR5 -->|0.5 ≤ confidence < 0.8| APPROVE2[✅ Approve: Execute with<br/>enhanced monitoring]
    GR5 -->|confidence < 0.5| HUMAN2[👤 Human approval required]
    
    GR5 -->|Also check| LOSS{Daily Loss Limit}
    LOSS -->|loss < ₹10,000| CONTINUE[Continue]
    LOSS -->|loss ≥ ₹10,000| PAUSE[⏸️ Pause autonomous pricing]
    
    REJECT1 --> LOG1[Log rejection reason]
    REJECT2 --> LOG1
    LOG1 --> END1([Decision Rejected])
    
    APPROVE1 --> EXEC[Execute Decision]
    APPROVE2 --> EXEC
    EXEC --> END2([Decision Executed])
    
    HUMAN1 --> END3([Awaiting Human])
    HUMAN2 --> END3
    QUEUE --> END4([Queued])
    PAUSE --> END5([System Paused])
    
    style GR1 fill:#fff9c4
    style GR2 fill:#fff9c4
    style GR3 fill:#fff9c4
    style GR4 fill:#fff9c4
    style GR5 fill:#fff9c4
    style LOSS fill:#fff9c4
    style APPROVE1 fill:#c8e6c9
    style APPROVE2 fill:#c8e6c9
    style REJECT1 fill:#ffcdd2
    style REJECT2 fill:#ffcdd2
    style HUMAN1 fill:#ffe0b2
    style HUMAN2 fill:#ffe0b2
```

## 4. Self-Correction Loop

```mermaid
flowchart TD
    START([Price Change Executed]) --> MON1[Monitor for 24 hours]
    MON1 --> MON2[Collect actual data:<br/>- Sales volume<br/>- Revenue<br/>- Margin]
    MON2 --> MON3[Compare vs predicted:<br/>- Expected: +5% revenue<br/>- Actual: -12% revenue]
    
    MON3 --> CHECK{Performance Check}
    CHECK -->|Deviation < 20%| SUCCESS([✅ Decision Successful])
    CHECK -->|Deviation ≥ 20%| ANOM[🚨 Anomaly Detected]
    
    ANOM --> CORR1[Correction Agent Activated]
    CORR1 --> CORR2[Gather evidence:<br/>- New competitor prices<br/>- Market conditions<br/>- Demand patterns]
    
    CORR2 --> CORR3[AI Root Cause Analysis]
    CORR3 --> CORR4{Classify Root Cause}
    
    CORR4 -->|Competitor Response| RC1["Competitor dropped further<br/>to ₹850 (we missed it)"]
    CORR4 -->|Demand Shift| RC2["Festival season started early<br/>Price sensitivity increased"]
    CORR4 -->|Pricing Error| RC3["Model overestimated<br/>demand elasticity"]
    CORR4 -->|External Shock| RC4["Supply chain disruption<br/>Competitor stockout"]
    
    RC1 --> CORR5[Generate corrective strategy]
    RC2 --> CORR5
    RC3 --> CORR5
    RC4 --> CORR5
    
    CORR5 --> CORR6[AI generates reasoning:<br/>"Reduce to ₹900 to match<br/>competitor and stop decline"]
    CORR6 --> CORR7[Calculate expected recovery:<br/>+15% demand vs current state]
    CORR7 --> CORR8[Assign confidence score]
    
    CORR8 --> COUNT{Correction Attempt Count}
    COUNT -->|Attempt 1 or 2| RESUBMIT[Re-submit to Supervisor]
    COUNT -->|Attempt 3| HUMAN[👤 Escalate to Human]
    
    RESUBMIT --> GUARD[Guardrail Validation]
    GUARD -->|Pass| EXEC[Execute Correction]
    GUARD -->|Fail| HUMAN
    
    EXEC --> LOG[Log correction with:<br/>- Original decision_id<br/>- Root cause<br/>- Corrective action<br/>- AI reasoning]
    LOG --> MON1
    
    HUMAN --> END1([Human Intervention])
    
    style MON1 fill:#f3e5f5
    style MON2 fill:#f3e5f5
    style MON3 fill:#f3e5f5
    style ANOM fill:#ffcdd2
    style CORR1 fill:#ffe0b2
    style CORR3 fill:#fff9c4
    style CORR5 fill:#ffe0b2
    style CORR6 fill:#fff9c4
    style SUCCESS fill:#c8e6c9
    style EXEC fill:#e8f5e9
```

## 5. AI Integration Points

```mermaid
flowchart LR
    subgraph "Decision Flow"
        D1[Market Event] --> D2[Pricing Decision]
        D2 --> D3[Execution]
        D3 --> D4[Monitoring]
        D4 --> D5[Correction]
    end
    
    subgraph "AI Layer"
        AI1[Natural Language<br/>Reasoning Generation]
        AI2[Demand Elasticity<br/>Prediction]
        AI3[Confidence<br/>Scoring]
        AI4[Root Cause<br/>Analysis]
        AI5[Corrective Strategy<br/>Reasoning]
    end
    
    subgraph "AI Services"
        LLM[Amazon Bedrock /<br/>OpenAI API]
        ML[ML Models /<br/>SageMaker]
    end
    
    D2 -->|"Generate explanation:<br/>'Competitor dropped 10%...<br/>Recommend ₹950...<br/>Expected +5% revenue'"| AI1
    AI1 <--> LLM
    
    D2 -->|"Predict demand change<br/>based on price change"| AI2
    AI2 <--> ML
    
    D2 -->|"Calculate confidence<br/>based on data quality,<br/>market volatility"| AI3
    AI3 <--> ML
    
    D5 -->|"Analyze why decision failed:<br/>'Competitor dropped further...<br/>Market volatility high'"| AI4
    AI4 <--> LLM
    
    D5 -->|"Generate corrective action:<br/>'Reduce to ₹900 to match...<br/>Expected +15% recovery'"| AI5
    AI5 <--> LLM
    
    AI1 --> OUT1[Decision Log with<br/>AI Reasoning]
    AI2 --> OUT2[Predicted Impact]
    AI3 --> OUT3[Confidence Score<br/>0.0 - 1.0]
    AI4 --> OUT4[Root Cause<br/>Classification]
    AI5 --> OUT5[Corrective Decision<br/>with Reasoning]
    
    style D2 fill:#fff4e1
    style D5 fill:#ffe0b2
    style AI1 fill:#f0f4c3
    style AI2 fill:#f0f4c3
    style AI3 fill:#f0f4c3
    style AI4 fill:#f0f4c3
    style AI5 fill:#f0f4c3
    style LLM fill:#dcedc8
    style ML fill:#dcedc8
```

## 6. Data Flow Architecture

```mermaid
flowchart TD
    subgraph "External Data Sources"
        EXT1[Competitor Websites<br/>Amazon.in, Flipkart]
        EXT2[Product Catalog<br/>HSN codes, costs, GST]
        EXT3[Sales Transactions<br/>Customer purchases]
    end
    
    subgraph "Ingestion Layer"
        ING1[Market Sensing Agent<br/>15-min polling]
        ING2[Product Data Loader<br/>Daily sync]
        ING3[Sales Tracker<br/>Real-time]
    end
    
    subgraph "Processing Layer"
        PROC1[Data Quality Validation<br/>- Reject >80% deviation<br/>- Flag stale data]
        PROC2[Event Classification<br/>- competitor_price_drop<br/>- demand_spike<br/>- festival_season]
        PROC3[Context Enrichment<br/>- Add category<br/>- Add margin<br/>- Add velocity]
    end
    
    subgraph "Decision Layer"
        DEC1[Pricing Strategy Agent<br/>- Compute scenarios<br/>- AI reasoning<br/>- Confidence scoring]
    end
    
    subgraph "Storage Layer"
        DB1[(PostgreSQL)]
        DB2[(Redis Cache)]
    end
    
    subgraph "Output Layer"
        OUT1[Storefront Database<br/>Updated prices]
        OUT2[Decision Logs<br/>Audit trail]
        OUT3[Dashboard<br/>Metrics & alerts]
    end
    
    EXT1 -->|Scrape| ING1
    EXT2 -->|Load| ING2
    EXT3 -->|Track| ING3
    
    ING1 --> PROC1
    ING2 --> DB1
    ING3 --> DB1
    
    PROC1 -->|Valid data| PROC2
    PROC1 -->|Invalid data| ALERT1[Alert: Data quality issue]
    
    PROC2 --> PROC3
    PROC3 --> DB2
    PROC3 --> DEC1
    
    DEC1 <--> DB1
    DEC1 <--> DB2
    DEC1 --> OUT1
    DEC1 --> OUT2
    
    OUT1 --> DB1
    OUT2 --> DB1
    DB1 --> OUT3
    
    style ING1 fill:#e1f5ff
    style PROC1 fill:#fff9c4
    style PROC2 fill:#fff9c4
    style PROC3 fill:#fff9c4
    style DEC1 fill:#fff4e1
    style DB1 fill:#e0e0e0
    style DB2 fill:#e0e0e0
```

## 7. Demo Scenario Flow

```mermaid
flowchart TD
    START([Demo Start]) --> SETUP[Setup: Product P123<br/>Current price: ₹1000<br/>Margin: 40%]
    
    SETUP --> SCENE1[🎬 Scene 1: Market Change]
    SCENE1 --> S1A[Competitor C456 drops price<br/>₹1000 → ₹900 (-10%)]
    S1A --> S1B[Market Sensing Agent detects<br/>within 15 minutes]
    S1B --> S1C[Show: CloudWatch logs<br/>Event: competitor_price_drop]
    
    S1C --> SCENE2[🎬 Scene 2: AI Decision]
    SCENE2 --> S2A[Pricing Strategy Agent analyzes]
    S2A --> S2B[Bedrock generates reasoning:<br/>'Competitor dropped 10%...<br/>Recommend ₹950 (37% margin)...<br/>Expected +5% revenue']
    S2B --> S2C[Show: Dashboard with AI reasoning<br/>Confidence: 75%]
    
    S2C --> SCENE3[🎬 Scene 3: Guardrails]
    SCENE3 --> S3A[Supervisor validates:<br/>✅ Margin 37% > 25% min<br/>✅ Discount 5% < 20% max<br/>✅ Confidence 75% > 50%]
    S3A --> S3B[Show: Guardrail checks passing]
    
    S3B --> SCENE4[🎬 Scene 4: Execution]
    SCENE4 --> S4A[Execution Agent updates:<br/>Price: ₹950 + 18% GST = ₹1121]
    S4A --> S4B[Show: DynamoDB updated<br/>Decision logged with reasoning]
    
    S4B --> SCENE5[🎬 Scene 5: Monitoring]
    SCENE5 --> S5A[Wait 24 hours simulation]
    S5A --> S5B[Actual: Sales -12%<br/>vs Predicted: +5%]
    S5B --> S5C[Show: Anomaly detected<br/>Performance alert triggered]
    
    S5C --> SCENE6[🎬 Scene 6: Self-Correction]
    SCENE6 --> S6A[Correction Agent investigates:<br/>Competitor dropped again to ₹850]
    S6A --> S6B[AI root cause analysis:<br/>'Missed second price drop...<br/>Recommend ₹900 to recover']
    S6B --> S6C[Show: Corrective decision<br/>with AI reasoning]
    S6C --> S6D[Re-execute through Supervisor]
    S6D --> S6E[Price updated to ₹900<br/>Linked to original decision]
    
    S6E --> SCENE7[🎬 Scene 7: Results]
    SCENE7 --> S7A[Show complete decision chain:<br/>Original → Underperformance → Correction]
    S7A --> S7B[Show metrics:<br/>- 85% autonomous decisions<br/>- 73% accuracy<br/>- Self-correction in 2 hours]
    
    S7B --> END([Demo Complete<br/>5 minutes total])
    
    style SCENE1 fill:#e1f5ff
    style SCENE2 fill:#fff4e1
    style SCENE3 fill:#ffcdd2
    style SCENE4 fill:#e8f5e9
    style SCENE5 fill:#f3e5f5
    style SCENE6 fill:#ffe0b2
    style SCENE7 fill:#c8e6c9
```

## How to Use These Diagrams

1. **Complete Decision Lifecycle Flow**: Use for explaining the entire system to judges
2. **Agent Interaction Architecture**: Use for technical architecture discussions
3. **Guardrail Validation Flow**: Use for explaining safety mechanisms
4. **Self-Correction Loop**: Use for demonstrating autonomous learning
5. **AI Integration Points**: Use for highlighting AI/ML components
6. **Data Flow Architecture**: Use for explaining data pipeline
7. **Demo Scenario Flow**: Use as script for live demonstration

## Rendering Instructions

These Mermaid diagrams can be rendered in:
- GitHub/GitLab markdown files (native support)
- VS Code with Mermaid extension
- Online: https://mermaid.live/
- Documentation sites (Docusaurus, MkDocs, etc.)
- Presentation tools (Marp, reveal.js)

For best results in presentations, export as SVG or PNG from mermaid.live with transparent background.
