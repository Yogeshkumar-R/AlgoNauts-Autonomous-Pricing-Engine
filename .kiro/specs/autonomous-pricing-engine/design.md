# Design Document: Self-Correcting Autonomous Pricing Engine for Indian SMEs

## 1. Problem Context: Indian SME Retail Ecosystem

Indian small and medium enterprises face a fragmented retail landscape where pricing decisions directly impact survival. Unlike large platform sellers on Amazon.in or Flipkart who use algorithmic pricing, most SMEs rely on manual, intuition-based pricing that leads to:

**Margin Erosion**: Manual price adjustments lag behind competitor moves by days or weeks, causing revenue loss of 8-15% in competitive categories.

**Competitive Disadvantage**: Platform sellers adjust prices multiple times daily using automated systems. SMEs checking competitor prices manually cannot match this velocity.

**Decision Paralysis**: Owners juggle inventory management, customer service, and operations—leaving no bandwidth for continuous pricing optimization. The result: prices stay static for months despite market shifts.

**Regional Complexity**: Indian markets vary dramatically by state, festival calendar, and local competition. A single pricing strategy fails across regions, but SMEs lack tools to manage regional variations.

**GST Compliance Overhead**: Every price change requires GST recalculation (5%, 12%, 18%, 28% rates), invoice updates, and platform synchronization—making frequent adjustments prohibitively time-consuming.

The core problem is not lack of information—it's lack of execution. SMEs need a system that doesn't just recommend prices but autonomously implements them within business constraints.

## 2. Gap in Existing Solutions

Current tools fail because they stop at insight generation:

**Analytics Dashboards** (Power BI, Tableau): Show competitor prices and trends but require humans to interpret data, decide on prices, and manually update systems. Decision-to-execution time: days.

**BI Tools** (Zoho Analytics, Metabase): Generate reports on pricing performance but provide no actionable automation. Owners still manually adjust prices across platforms.

**Pricing SaaS** (Prisync, Competera): Offer price recommendations but require approval workflows and manual implementation. The "last mile" of execution remains manual.

**E-commerce Platform Tools** (Shopify pricing apps): Limited to single-platform optimization, no cross-platform intelligence, and still require manual review and approval.

The gap: No system autonomously senses market changes, decides optimal pricing, executes updates, monitors outcomes, and self-corrects—all within business guardrails and without human intervention for routine decisions.

## 3. Proposed System: Self-Correcting Autonomous Pricing Engine

### System Definition

An autonomous multi-agent system that operates as a retail pricing operator, not an advisor. The system continuously executes a decision lifecycle:

**Market Sensing** → **Pricing Decision** → **Execution** → **Monitoring** → **Correction**

### Operational Philosophy

The system behaves like an experienced pricing manager who:
- Monitors competitor prices continuously
- Adjusts prices within predefined margins and discount limits
- Implements changes immediately to a simulated storefront
- Tracks sales performance and margin impact
- Corrects strategy when outcomes deviate from expectations
- Escalates only exceptional cases requiring human judgment

### Key Differentiators

**Autonomous Execution**: Prices update automatically in the simulated storefront without approval workflows for routine decisions.

**Self-Correction**: When pricing decisions underperform (sales drop, margins compress), the system automatically revises strategy rather than waiting for human intervention.

**Decision Traceability**: Every price change is logged with trigger, reasoning, expected impact, and actual outcome—enabling full audit trails.

**Guardrail-Bounded**: Operates within business-defined constraints (minimum margin, maximum discount, price change velocity) to prevent harmful decisions.

## 4. Agentic Architecture

The system uses a supervisor-worker pattern with specialized agents handling distinct phases of the decision lifecycle.

### Agent Roles and Responsibilities

**Supervisor Agent**
- Orchestrates the decision lifecycle across all agents
- Routes market signals to appropriate decision agents
- Enforces guardrails before execution
- Manages escalation to human operators for edge cases
- Coordinates correction loops when performance degrades

**Market Sensing Agent**
- Monitors competitor prices from simulated data feeds (Amazon.in, Flipkart, local retailers)
- Detects significant price changes (>5% movement, new competitor entry)
- Tracks inventory levels and sales velocity
- Identifies festival seasons and regional demand patterns
- Publishes market events to Supervisor

**Pricing Strategy Agent**
- Receives market events and current business state
- Computes optimal price using cost-plus, competitive positioning, and demand elasticity
- Generates multiple pricing scenarios (aggressive, balanced, conservative)
- Calculates expected impact on revenue, profit, and market share
- Recommends price with confidence score and reasoning

**Execution Agent**
- Receives approved pricing decisions from Supervisor
- Calculates GST-inclusive prices for Indian compliance
- Updates simulated storefront database (product catalog, pricing tables)
- Generates pricing change logs with timestamps and decision IDs
- Confirms execution success or reports failures

**Monitoring Agent**
- Tracks sales performance post-price change (hourly, daily aggregates)
- Compares actual outcomes vs predicted impact
- Detects anomalies (sales collapse, margin compression, inventory stagnation)
- Calculates decision accuracy metrics
- Triggers correction events when thresholds breached

**Correction Agent**
- Receives underperformance signals from Monitoring Agent
- Analyzes root cause (price too high, competitor response, demand shift)
- Generates corrective pricing strategy
- Submits revised pricing decision to Supervisor
- Logs correction rationale and expected recovery

### Agent Interaction Flow

```
Market Sensing Agent → [price change detected] → Supervisor Agent
                                                      ↓
Supervisor Agent → [evaluate decision] → Pricing Strategy Agent
                                                      ↓
Pricing Strategy Agent → [optimal price + reasoning] → Supervisor Agent
                                                      ↓
Supervisor Agent → [check guardrails] → [pass] → Execution Agent
                                      → [fail] → [escalate to human]
                                                      ↓
Execution Agent → [update storefront] → [log decision] → Monitoring Agent
                                                      ↓
Monitoring Agent → [track performance] → [detect underperformance] → Correction Agent
                                                      ↓
Correction Agent → [revised strategy] → Supervisor Agent → [re-execute cycle]
```

### Agent Communication Protocol

Agents communicate via structured messages containing:
- **Event Type**: market_change, pricing_decision, execution_complete, performance_alert, correction_required
- **Payload**: relevant data (product_id, old_price, new_price, confidence_score, etc.)
- **Metadata**: timestamp, agent_id, correlation_id for tracing decision chains
- **Priority**: routine, urgent, critical (affects processing order)

## 5. Decision Lifecycle: Step-by-Step Flow

### Phase 1: Market Event Detection

**Trigger**: Competitor price drops 10% on similar product

**Market Sensing Agent**:
1. Scrapes competitor data from simulated feeds (every 15 minutes)
2. Compares current prices vs historical baseline
3. Detects significant deviation (>5% change)
4. Enriches event with context (competitor identity, product category, timing)
5. Publishes `market_change` event to Supervisor

**Output**: `{"event": "competitor_price_drop", "product_id": "P123", "competitor": "C456", "old_price": 1000, "new_price": 900, "change_pct": -10}`

### Phase 2: Pricing Decision

**Supervisor Agent**:
1. Receives market event
2. Retrieves current product state (cost, inventory, sales velocity)
3. Routes to Pricing Strategy Agent with context

**Pricing Strategy Agent**:
1. Loads product cost structure (base cost ₹600, target margin 30%)
2. Analyzes competitor positioning (now ₹900 vs our ₹1000)
3. Computes scenarios:
   - **Aggressive**: Match competitor at ₹900 (margin 33%)
   - **Balanced**: Price at ₹950 (margin 37%)
   - **Conservative**: Hold at ₹1000 (margin 40%)
4. Estimates impact using demand elasticity model
5. Selects balanced strategy (₹950) with 75% confidence
6. Generates reasoning: "Competitor dropped 10%. Matching partially maintains margin while staying competitive."

**Output**: `{"recommended_price": 950, "strategy": "balanced", "confidence": 0.75, "expected_revenue_change": +5%, "reasoning": "..."}`

### Phase 3: Guardrail Validation

**Supervisor Agent**:
1. Checks minimum margin constraint (30% required, 37% proposed ✓)
2. Checks maximum discount limit (15% max, 5% proposed ✓)
3. Checks price change velocity (max 2 changes/day, 0 today ✓)
4. Checks approval threshold (changes >20% require human, 5% proposed ✓)
5. All guardrails pass → approve for execution

**Output**: `{"guardrail_status": "pass", "approved": true}`

### Phase 4: Execution

**Execution Agent**:
1. Receives approved decision
2. Calculates GST-inclusive price (₹950 + 18% GST = ₹1121)
3. Updates simulated storefront database:
   ```sql
   UPDATE products 
   SET price_excl_gst = 950, 
       price_incl_gst = 1121, 
       last_updated = NOW()
   WHERE product_id = 'P123';
   ```
4. Logs decision to audit trail:
   ```json
   {
     "decision_id": "D789",
     "product_id": "P123",
     "old_price": 1000,
     "new_price": 950,
     "trigger": "competitor_price_drop",
     "executed_at": "2024-03-15T10:30:00Z",
     "reasoning": "..."
   }
   ```
5. Confirms execution success to Supervisor

**Output**: `{"execution_status": "success", "decision_id": "D789"}`

### Phase 5: Performance Monitoring

**Monitoring Agent**:
1. Tracks sales for 24 hours post-change
2. Compares actual vs predicted outcomes:
   - **Predicted**: +5% revenue increase
   - **Actual**: +8% revenue increase (better than expected)
3. Calculates decision accuracy: 92% (within confidence interval)
4. No anomalies detected → mark decision as successful

**Output**: `{"decision_id": "D789", "performance": "success", "accuracy": 0.92}`

### Phase 6: Self-Correction (Triggered on Underperformance)

**Scenario**: Price change causes sales to drop 15% instead of increasing

**Monitoring Agent**:
1. Detects negative outcome (sales -15% vs predicted +5%)
2. Publishes `performance_alert` event to Supervisor

**Supervisor Agent**:
1. Routes alert to Correction Agent

**Correction Agent**:
1. Analyzes root cause:
   - Competitor dropped price further to ₹850
   - Our ₹950 price now 12% higher than market leader
2. Generates corrective strategy: reduce to ₹900 (margin 33%)
3. Submits revised decision to Supervisor

**Supervisor Agent**:
1. Validates guardrails (still within limits)
2. Approves correction
3. Routes to Execution Agent

**Execution Agent**:
1. Updates price to ₹900
2. Logs correction with reference to original decision

**Output**: System self-corrects within 2 hours of detecting underperformance

## 6. Data Strategy: Public and Synthetic Sources

### Product Data

**Source**: Open product datasets (Kaggle, data.gov.in)
- Product catalog with categories, descriptions, base costs
- HSN codes for GST compliance
- Inventory levels (synthetic generation)

**Schema**:
```python
{
  "product_id": "P123",
  "name": "Wireless Mouse",
  "category": "Electronics",
  "hsn_code": "8471",
  "base_cost": 600,
  "gst_rate": 0.18,
  "inventory_units": 150
}
```

### Competitor Price Data

**Source**: Simulated competitor feeds
- Generate realistic price distributions for 5-10 competitors
- Simulate price changes based on market dynamics (festival discounts, inventory clearance)
- Model competitor strategies (aggressive, balanced, premium)

**Generation Logic**:
```python
# Competitor prices distributed around base cost with positioning multipliers
base_cost = 600
competitor_prices = {
  "budget_seller": base_cost * 1.25,  # ₹750
  "mid_market": base_cost * 1.50,     # ₹900
  "premium": base_cost * 1.80         # ₹1080
}
# Add random variation ±10% to simulate market dynamics
```

### Sales Data

**Source**: Synthetic generation using demand elasticity models
- Generate baseline sales volume for each product
- Apply price elasticity (e.g., 10% price increase → 8% demand decrease)
- Add seasonal patterns (festival spikes, off-season dips)
- Inject noise to simulate real-world variability

**Generation Logic**:
```python
# Baseline demand at reference price
baseline_demand = 100 units/day
price_elasticity = -0.8

# Calculate demand at new price
price_change_pct = (new_price - reference_price) / reference_price
demand_change_pct = price_elasticity * price_change_pct
new_demand = baseline_demand * (1 + demand_change_pct)
```

### ONDC Compatibility

Structure data schemas to align with Open Network for Digital Commerce (ONDC) standards:
- Product catalog format compatible with ONDC item schema
- Pricing updates follow ONDC pricing structure
- Order and fulfillment data match ONDC transaction format

This ensures future integration with India's open commerce network.

### Data Feasibility

All data sources are:
- **Publicly available** or **synthetically generated**
- **No proprietary APIs** or paid data services required
- **Realistic enough** to demonstrate system behavior
- **Buildable within 9 days** using Python data generation scripts

## 7. Prototype Scope: What Will and Won't Be Built

### WILL Be Built (9-Day Feasibility)

**Autonomous Pricing Loop**:
- Market sensing agent monitoring simulated competitor feeds
- Pricing strategy agent computing optimal prices
- Execution agent updating simulated storefront database
- Monitoring agent tracking performance metrics
- Correction agent triggering strategy adjustments
- Complete decision lifecycle from detection to correction

**Simulated Storefront**:
- PostgreSQL database representing product catalog
- Price update APIs simulating e-commerce platform
- Sales transaction generator simulating customer purchases
- Inventory tracking system
- GST calculation engine for Indian compliance

**Monitoring and Observability**:
- Decision log database (all pricing decisions with reasoning)
- Performance dashboard showing decision outcomes
- Confidence score tracking
- Guardrail violation alerts
- Decision trace viewer (follow a decision through entire lifecycle)

**Guardrail System**:
- Minimum margin enforcement (e.g., never go below 25%)
- Maximum discount limits (e.g., max 20% off)
- Price change velocity limits (e.g., max 3 changes per day)
- Approval thresholds (e.g., changes >30% require human review)
- Rollback conditions (e.g., auto-revert if sales drop >20%)

**Agent Orchestration**:
- Supervisor agent coordinating workflow
- Message passing between agents
- Event-driven architecture using queues
- Parallel processing for multiple products

**Self-Correction Mechanism**:
- Performance anomaly detection
- Root cause analysis (basic heuristics)
- Corrective strategy generation
- Automatic re-execution of pricing cycle

### Will NOT Be Built (Out of Scope)

**Full ERP Integrations**:
- No real Tally or Zoho Books integration
- No actual e-commerce platform APIs (Shopify, WooCommerce)
- Simulated interfaces only

**Enterprise Dashboard**:
- No production-grade UI with authentication
- Basic monitoring dashboard sufficient for demo
- Focus on backend decision engine, not frontend polish

**Complex Forecasting Stack**:
- No deep learning demand forecasting models
- Simple elasticity-based models sufficient
- No time series forecasting (ARIMA, Prophet)

**Multi-Tenant Architecture**:
- Single business simulation only
- No user management or access control
- Prototype demonstrates concept for one SME

**Real-Time Data Pipelines**:
- Batch processing acceptable (15-minute intervals)
- No streaming data infrastructure (Kafka, Kinesis)
- Simulated data feeds sufficient

**Advanced ML Models**:
- No reinforcement learning for pricing optimization
- Rule-based and heuristic strategies sufficient
- Focus on decision execution, not ML sophistication

### Prototype Deliverables

1. **Working System**: Autonomous pricing engine running end-to-end decision loops
2. **Simulated Environment**: Storefront database with realistic product and sales data
3. **Decision Logs**: Complete audit trail of all pricing decisions
4. **Monitoring Dashboard**: Basic UI showing system activity and performance
5. **Documentation**: Architecture diagrams, decision flow documentation, setup guide
6. **Demo Scenario**: Pre-configured scenario showing market change → autonomous response → self-correction

## 8. Observability and Guardrails

### Decision Logging

Every pricing decision generates a structured log entry:

```json
{
  "decision_id": "D789",
  "timestamp": "2024-03-15T10:30:00Z",
  "product_id": "P123",
  "trigger": {
    "type": "competitor_price_drop",
    "competitor_id": "C456",
    "competitor_price": 900
  },
  "decision": {
    "old_price_excl_gst": 1000,
    "new_price_excl_gst": 950,
    "old_price_incl_gst": 1180,
    "new_price_incl_gst": 1121,
    "strategy": "balanced",
    "confidence_score": 0.75
  },
  "reasoning": "Competitor dropped 10%. Matching partially maintains margin while staying competitive.",
  "expected_impact": {
    "revenue_change_pct": 5,
    "profit_change_pct": 3,
    "demand_change_pct": 8
  },
  "guardrails": {
    "min_margin_check": "pass",
    "max_discount_check": "pass",
    "velocity_check": "pass",
    "approval_required": false
  },
  "execution": {
    "status": "success",
    "executed_at": "2024-03-15T10:30:15Z"
  },
  "monitoring": {
    "actual_revenue_change_pct": 8,
    "actual_profit_change_pct": 5,
    "decision_accuracy": 0.92,
    "performance_status": "success"
  }
}
```

### Confidence Scoring

Each pricing decision includes a confidence score (0-1) based on:
- **Data Quality**: Completeness and freshness of competitor data
- **Model Certainty**: Variance in predicted outcomes across scenarios
- **Historical Accuracy**: Past performance of similar decisions
- **Market Volatility**: Stability of recent price movements

**Confidence Thresholds**:
- **High (>0.8)**: Execute autonomously
- **Medium (0.5-0.8)**: Execute with enhanced monitoring
- **Low (<0.5)**: Escalate to human review

### Margin Protection Rules

**Hard Constraints** (never violated):
- Minimum margin: 25% (configurable per product category)
- Never price below cost + GST + platform fees
- Maximum single-day loss: ₹10,000 across all products

**Soft Constraints** (trigger warnings):
- Target margin: 35% (system tries to maintain but can go lower)
- Preferred discount range: 5-15% (can exceed with justification)

### Rollback Conditions

System automatically reverts price changes if:
- Sales volume drops >20% within 24 hours
- Profit margin falls below minimum threshold
- Inventory depletion rate exceeds safety stock levels
- Competitor prices return to original levels (false alarm)

**Rollback Process**:
1. Monitoring Agent detects rollback condition
2. Supervisor Agent validates condition severity
3. Execution Agent reverts to previous price
4. Correction Agent analyzes why decision failed
5. System logs rollback event with root cause

### Escalation Triggers

Human intervention required when:
- Confidence score <0.5 for critical products
- Guardrail violations detected
- Repeated rollbacks (>3 times in 24 hours for same product)
- Anomalous market conditions (e.g., all competitors drop prices 50%)
- System performance degradation (decision accuracy <60% over 7 days)

### Audit Trail

Complete traceability for every decision:
- **Decision Chain**: Link from market event → pricing decision → execution → monitoring → correction
- **Agent Attribution**: Which agent made each decision component
- **Timing**: Latency at each stage (detection to execution time)
- **Outcome**: Predicted vs actual performance
- **Corrections**: History of adjustments made to original decision

## 9. Expected Impact

### Economic Impact for Indian SMEs

**Faster Pricing Decisions**:
- **Current State**: Manual price checks 1-2 times per week, decision-to-execution time 2-5 days
- **With System**: Continuous monitoring, decision-to-execution time <5 minutes
- **Impact**: Capture time-sensitive opportunities (competitor stockouts, festival demand spikes)

**Reduced Manual Dependency**:
- **Current State**: Owner spends 5-10 hours/week on pricing decisions
- **With System**: Autonomous operation for 90% of routine decisions
- **Impact**: Owner focuses on strategy, customer relationships, and business growth

**Improved Competitiveness**:
- **Current State**: SMEs lag platform sellers by days in price adjustments
- **With System**: Match platform seller velocity with autonomous updates
- **Impact**: Retain price-sensitive customers, reduce cart abandonment

**Margin Optimization**:
- **Current State**: Static pricing leaves money on table or erodes margins
- **With System**: Dynamic pricing balances competitiveness and profitability
- **Impact**: Estimated 5-12% margin improvement through optimized pricing

### Operational Impact

**Decision Quality**:
- Consistent application of pricing strategy (no human fatigue or bias)
- Data-driven decisions using real-time competitor intelligence
- Self-correction when strategies underperform

**Risk Mitigation**:
- Guardrails prevent catastrophic pricing errors
- Rollback mechanisms limit downside of bad decisions
- Audit trails enable post-mortem analysis

**Scalability**:
- System handles 100s-1000s of products simultaneously
- No marginal cost to monitor additional competitors
- Automated execution eliminates manual bottleneck

### Prototype Validation Metrics

Success criteria for 9-day prototype:
1. **Autonomy**: System executes 80%+ of pricing decisions without human intervention
2. **Responsiveness**: Detection-to-execution time <10 minutes for market changes
3. **Accuracy**: Decision outcomes within 20% of predicted impact
4. **Self-Correction**: System automatically adjusts strategy when performance degrades
5. **Observability**: Complete decision trace for every pricing change

### Real-World Constraints Addressed

**GST Compliance**: All prices calculated with correct GST rates (5%, 12%, 18%, 28%)

**Regional Variations**: System supports different pricing strategies by region (though prototype focuses on single region)

**Festival Seasonality**: Pricing strategies account for Indian festival calendar (Diwali, Holi, etc.)

**Platform Fees**: Cost calculations include marketplace commissions (Amazon, Flipkart take 10-20%)

**Inventory Constraints**: Pricing decisions consider stock levels (aggressive discounts for slow-moving inventory)

**Competitive Dynamics**: System responds to local competition, not just national platforms

## 10. Technical Architecture

### System Components

**Agent Runtime**:
- Python-based agent framework (LangGraph or custom orchestration)
- Asynchronous message passing between agents
- Event-driven architecture using queues (Redis or in-memory)

**Data Storage**:
- PostgreSQL for product catalog, pricing history, decision logs
- Redis for real-time state (current prices, competitor data cache)
- JSON files for configuration (guardrails, agent parameters)

**Simulated Storefront**:
- Flask/FastAPI REST API simulating e-commerce platform
- Endpoints: GET /products, POST /update_price, GET /sales
- Database-backed product catalog with price versioning

**Monitoring Dashboard**:
- Streamlit or Gradio for rapid UI development
- Real-time decision log viewer
- Performance metrics charts (sales, margins, decision accuracy)
- Agent activity monitor

**Data Generation**:
- Python scripts to generate synthetic competitor prices
- Sales simulator using elasticity models
- Market event generator (price changes, demand shifts)

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Supervisor Agent                      │
│              (Orchestration & Guardrails)                │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Market Sensing   │  │ Pricing Strategy │  │ Execution Agent  │
│     Agent        │  │      Agent       │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  PostgreSQL DB   │
                    │  (Products,      │
                    │   Decisions,     │
                    │   Sales)         │
                    └──────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
┌──────────────────┐                      ┌──────────────────┐
│ Monitoring Agent │                      │ Correction Agent │
└──────────────────┘                      └──────────────────┘
```

### Technology Choices (9-Day Feasibility)

**Agent Framework**: LangGraph (if using LLMs) or custom Python classes
- Rationale: Rapid development, flexible orchestration

**Database**: PostgreSQL + Redis
- Rationale: Familiar, reliable, sufficient for prototype scale

**API Framework**: FastAPI
- Rationale: Fast development, automatic API docs, async support

**Dashboard**: Streamlit
- Rationale: Python-native, rapid UI development, no frontend expertise needed

**Data Generation**: Pandas + NumPy
- Rationale: Efficient synthetic data generation, statistical modeling

**Deployment**: Docker Compose
- Rationale: Easy local development, reproducible environment

### Development Timeline (9 Days)

**Days 1-2**: Data generation and simulated storefront
- Create product catalog with synthetic data
- Build competitor price simulator
- Implement sales transaction generator
- Set up PostgreSQL schema

**Days 3-4**: Core agent implementation
- Build Market Sensing Agent (competitor monitoring)
- Build Pricing Strategy Agent (decision logic)
- Build Execution Agent (price updates)
- Implement Supervisor Agent (orchestration)

**Days 5-6**: Monitoring and self-correction
- Build Monitoring Agent (performance tracking)
- Build Correction Agent (strategy adjustment)
- Implement guardrail validation
- Add decision logging

**Days 7-8**: Integration and testing
- Connect all agents in decision loop
- Test end-to-end scenarios
- Implement rollback mechanisms
- Build monitoring dashboard

**Day 9**: Documentation and demo preparation
- Create architecture diagrams
- Write setup and usage documentation
- Prepare demo scenario
- Record system walkthrough

This design prioritizes working software over comprehensive features, demonstrating autonomous decision execution within hackathon constraints.
