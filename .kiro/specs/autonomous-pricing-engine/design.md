# Design Document: Autonomous Pricing Engine - Hackathon Prototype

**Prototype Scope**: 4-5 day hackathon build (Feb 27 - Mar 3)  
**Budget**: $100 AWS credits  
**Goal**: Demonstrate autonomous pricing concept with minimal viable architecture

## 1. Problem Statement (Simplified)

SMEs manually check competitor prices and adjust their own prices, leading to:
- Slow response to market changes (days/weeks delay)
- Missed opportunities during competitor price drops
- No systematic decision tracking

**Core Value Proposition**: Autonomous system that monitors competitor prices, makes pricing decisions, executes updates, and logs everything—without human intervention for routine decisions.

## 2. Hackathon Prototype Scope

### What We WILL Build (Core Demo)

**Autonomous Pricing Loop**:
- Monitor competitor prices (from CSV files)
- Make pricing decisions using rule-based logic
- Execute price updates to simulated product catalog
- Log all decisions with reasoning
- One guardrail: minimum margin protection

**Simple Architecture**:
- 2-3 Lambda functions (not 6 agents)
- S3 for data storage (CSV files)
- EventBridge for hourly scheduling
- CloudWatch for logging
- No database, no AI/LLM, no dashboard

**Demo Scenario**:
- 10 products, 3 competitors
- Simulate 1 competitor price drop
- Show autonomous price adjustment
- Display decision log with reasoning
- Prove end-to-end automation in 5 minutes

### What We Will NOT Build (Out of Scope)

❌ Multi-agent system (too complex)  
❌ AI/LLM integration (costs money, adds complexity)  
❌ Self-correction loop (too ambitious)  
❌ Monitoring agent (just log decisions)  
❌ Real-time processing (batch hourly is fine)  
❌ Database (CSV/JSON files sufficient)  
❌ Dashboard UI (CLI output is enough)  
❌ GST calculations (flat pricing)  
❌ Festival seasonality  
❌ ONDC integration  
❌ Multiple pricing strategies  
❌ Confidence scoring  
❌ Rollback mechanisms

## 3. Simplified Architecture

### System Components (Minimal)

**Component 1: Price Monitor (Lambda)**
- Reads competitor prices from S3 CSV file
- Compares against our current prices
- Detects significant changes (>5% price drop)
- Triggers pricing decision if change detected

**Component 2: Price Decision Engine (Lambda)**
- Receives price change event
- Applies simple rule-based logic:
  - If competitor drops price by X%, match 50% of the drop
  - Never go below minimum margin (30%)
  - Calculate new price
- Generates decision record with reasoning (template-based)
- Writes decision to S3 decision log

**Component 3: Price Executor (Lambda)**
- Reads approved decisions from S3
- Updates product catalog CSV file
- Logs execution timestamp
- Outputs summary to CloudWatch

**Data Storage (S3)**:
- `products.csv` - Product catalog with current prices
- `competitor_prices.csv` - Competitor price data
- `decisions/` - Decision logs (JSON files)
- `config.json` - Business rules and guardrails

**Orchestration (EventBridge)**:
- Hourly schedule triggers Price Monitor
- Price Monitor invokes Decision Engine if needed
- Decision Engine invokes Executor

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  EventBridge Rule                    │
│              (Hourly: 0 * * * *)                     │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│            Lambda: Price Monitor                     │
│  - Read competitor_prices.csv from S3                │
│  - Compare with products.csv                         │
│  - Detect changes >5%                                │
└─────────────────────────────────────────────────────┘
                         │
                         ▼ (if change detected)
┌─────────────────────────────────────────────────────┐
│         Lambda: Price Decision Engine                │
│  - Apply rule-based pricing logic                    │
│  - Check minimum margin guardrail                    │
│  - Generate decision with reasoning                  │
│  - Write to S3: decisions/{timestamp}.json           │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Lambda: Price Executor                     │
│  - Read decision from S3                             │
│  - Update products.csv                               │
│  - Log to CloudWatch                                 │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                    S3 Bucket                         │
│  - products.csv (updated prices)                     │
│  - competitor_prices.csv (market data)               │
│  - decisions/*.json (audit trail)                    │
│  - config.json (business rules)                      │
└─────────────────────────────────────────────────────┘
```

## 4. Rule-Based Pricing Logic (No AI/ML)

### Pricing Decision Algorithm

```python
def calculate_new_price(product, competitor_prices, config):
    """
    Simple rule-based pricing logic
    """
    # Get current state
    our_price = product['price']
    our_cost = product['cost']
    min_margin = config['min_margin_pct']  # e.g., 30%
    
    # Find lowest competitor price
    lowest_competitor = min(competitor_prices)
    
    # Calculate price change
    competitor_drop_pct = (our_price - lowest_competitor) / our_price * 100
    
    # Decision rules
    if competitor_drop_pct < 5:
        # Small change, ignore
        return {
            'action': 'no_change',
            'new_price': our_price,
            'reasoning': f'Competitor price change <5% ({competitor_drop_pct:.1f}%), within acceptable range'
        }
    
    # Match 50% of competitor drop
    price_adjustment = (our_price - lowest_competitor) * 0.5
    proposed_price = our_price - price_adjustment
    
    # Check minimum margin guardrail
    min_price = our_cost * (1 + min_margin / 100)
    
    if proposed_price < min_price:
        # Violates margin, use minimum acceptable price
        final_price = min_price
        reasoning = f'Competitor dropped {competitor_drop_pct:.1f}% to ₹{lowest_competitor}. ' \
                   f'Proposed ₹{proposed_price:.0f} violates {min_margin}% margin floor. ' \
                   f'Setting to minimum ₹{final_price:.0f} (margin protected).'
    else:
        # Safe to adjust
        final_price = proposed_price
        margin_pct = (final_price - our_cost) / our_cost * 100
        reasoning = f'Competitor dropped {competitor_drop_pct:.1f}% to ₹{lowest_competitor}. ' \
                   f'Matching 50% of drop: ₹{our_price} → ₹{final_price:.0f}. ' \
                   f'Maintains {margin_pct:.1f}% margin (above {min_margin}% floor).'
    
    return {
        'action': 'price_change',
        'old_price': our_price,
        'new_price': round(final_price, 2),
        'reasoning': reasoning,
        'competitor_price': lowest_competitor,
        'margin_protected': proposed_price < min_price
    }
```

### Template-Based Reasoning

Instead of AI-generated explanations, use simple templates:

```python
REASONING_TEMPLATES = {
    'competitor_drop': 'Competitor {competitor_id} dropped price {drop_pct}% to ₹{new_price}. '
                      'Adjusting our price from ₹{old_price} to ₹{new_price} to remain competitive '
                      'while maintaining {margin}% margin.',
    
    'margin_protected': 'Proposed price ₹{proposed} would violate {min_margin}% margin floor. '
                       'Setting to minimum acceptable price ₹{final} (cost ₹{cost} + {margin}% margin).',
    
    'no_change': 'Competitor price change {change_pct}% is within acceptable threshold. '
                'Maintaining current price ₹{price}.'
}
```

## 5. Decision Flow (Simplified)

### Step 1: Price Monitoring (Hourly)

**Trigger**: EventBridge rule fires every hour

**Price Monitor Lambda**:
1. Read `competitor_prices.csv` from S3
2. Read `products.csv` from S3
3. For each product, compare our price vs competitor prices
4. If any competitor price dropped >5%, trigger decision

**Example Data**:
```csv
# competitor_prices.csv
product_id,competitor_a,competitor_b,competitor_c,timestamp
P001,899,950,920,2024-02-27T10:00:00Z
P002,1499,1550,1480,2024-02-27T10:00:00Z
```

### Step 2: Pricing Decision

**Price Decision Engine Lambda**:
1. Receive product_id and competitor prices
2. Load product cost and current price
3. Apply rule-based logic (see Section 4)
4. Check minimum margin guardrail
5. Generate decision record
6. Write to S3: `decisions/{timestamp}_{product_id}.json`

**Decision Record Example**:
```json
{
  "decision_id": "D_20240227_100530_P001",
  "timestamp": "2024-02-27T10:05:30Z",
  "product_id": "P001",
  "product_name": "Wireless Mouse",
  "trigger": "competitor_price_drop",
  "old_price": 1000,
  "new_price": 950,
  "competitor_lowest": 899,
  "cost": 600,
  "margin_pct": 58.3,
  "reasoning": "Competitor dropped 10.1% to ₹899. Matching 50% of drop: ₹1000 → ₹950. Maintains 58.3% margin (above 30% floor).",
  "guardrail_status": "pass",
  "executed": false
}
```

### Step 3: Price Execution

**Price Executor Lambda**:
1. Read pending decisions from S3
2. Update `products.csv` with new prices
3. Mark decision as executed
4. Log to CloudWatch

**Updated Product Record**:
```csv
# products.csv
product_id,name,cost,price,last_updated
P001,Wireless Mouse,600,950,2024-02-27T10:06:00Z
P002,Keyboard,800,1500,2024-02-26T15:00:00Z
```

### Step 4: Audit Trail

All decisions logged to S3 in `decisions/` folder:
- `decisions/2024-02-27_100530_P001.json`
- `decisions/2024-02-27_140215_P003.json`
- etc.

Can be queried later for:
- What price changes were made?
- Why was each decision made?
- Which products are most frequently adjusted?
- Are guardrails working?

## 6. Data Model (CSV-Based)

### products.csv
```csv
product_id,name,category,cost,price,min_margin_pct,last_updated
P001,Wireless Mouse,Electronics,600,1000,30,2024-02-27T09:00:00Z
P002,USB Keyboard,Electronics,800,1500,30,2024-02-27T09:00:00Z
P003,Laptop Stand,Accessories,400,800,35,2024-02-27T09:00:00Z
P004,Webcam HD,Electronics,1200,2200,30,2024-02-27T09:00:00Z
P005,Phone Case,Accessories,150,400,40,2024-02-27T09:00:00Z
P006,Screen Protector,Accessories,80,250,45,2024-02-27T09:00:00Z
P007,HDMI Cable,Electronics,200,500,35,2024-02-27T09:00:00Z
P008,Power Bank,Electronics,900,1800,30,2024-02-27T09:00:00Z
P009,Bluetooth Speaker,Electronics,1500,2800,30,2024-02-27T09:00:00Z
P010,Desk Lamp,Accessories,600,1200,35,2024-02-27T09:00:00Z
```

### competitor_prices.csv
```csv
product_id,competitor_a,competitor_b,competitor_c,timestamp
P001,950,980,920,2024-02-27T10:00:00Z
P002,1480,1520,1450,2024-02-27T10:00:00Z
P003,780,820,750,2024-02-27T10:00:00Z
P004,2150,2200,2100,2024-02-27T10:00:00Z
P005,380,420,390,2024-02-27T10:00:00Z
P006,240,260,230,2024-02-27T10:00:00Z
P007,480,520,490,2024-02-27T10:00:00Z
P008,1750,1820,1700,2024-02-27T10:00:00Z
P009,2700,2850,2650,2024-02-27T10:00:00Z
P010,1150,1220,1180,2024-02-27T10:00:00Z
```

### config.json
```json
{
  "business_rules": {
    "default_min_margin_pct": 30,
    "price_change_threshold_pct": 5,
    "competitor_match_ratio": 0.5
  },
  "guardrails": {
    "min_margin_pct": 30,
    "max_price_drop_pct": 20,
    "max_changes_per_day": 3
  }
}
```

### Decision Log Example
```json
{
  "decision_id": "D_20240227_100530_P001",
  "timestamp": "2024-02-27T10:05:30Z",
  "product_id": "P001",
  "product_name": "Wireless Mouse",
  "trigger": "competitor_price_drop",
  "old_price": 1000,
  "new_price": 950,
  "cost": 600,
  "margin_pct": 58.3,
  "competitor_lowest": 920,
  "competitor_drop_pct": 8.0,
  "reasoning": "Competitor dropped 8.0% to ₹920. Matching 50% of drop: ₹1000 → ₹950. Maintains 58.3% margin (above 30% floor).",
  "guardrail_checks": {
    "min_margin": "pass",
    "max_drop": "pass"
  },
  "executed": true,
  "executed_at": "2024-02-27T10:06:15Z"
}
```

## 7. AWS Services & Cost Estimate

### Services Used (Free Tier Friendly)

**AWS Lambda** (3 functions):
- Price Monitor: Runs hourly, ~10 seconds execution
- Price Decision Engine: Triggered on-demand, ~5 seconds
- Price Executor: Triggered on-demand, ~3 seconds
- **Cost**: Free tier covers 1M requests + 400,000 GB-seconds/month
- **Estimated**: ~720 invocations/month (hourly) = $0

**Amazon S3**:
- Store CSV files and decision logs
- ~100 KB per decision log × 720 decisions = ~72 MB/month
- **Cost**: Free tier covers 5GB storage + 20,000 GET requests
- **Estimated**: $0

**Amazon EventBridge**:
- 1 rule firing hourly (720 times/month)
- **Cost**: Free tier covers 1M events/month
- **Estimated**: $0

**Amazon CloudWatch**:
- Logs from Lambda executions
- ~10 KB per execution × 720 = ~7.2 MB/month
- **Cost**: Free tier covers 5GB logs
- **Estimated**: $0

**Total Monthly Cost**: $0 (within free tier)  
**Demo Cost**: $0  
**Budget Remaining**: $100 (untouched)

## 8. Demo Scenario (5-Minute Walkthrough)

### Setup (Pre-Demo)

1. Upload initial data to S3:
   - `products.csv` (10 products, current prices)
   - `competitor_prices.csv` (baseline competitor prices)
   - `config.json` (business rules)

2. Deploy Lambda functions via AWS SAM or Serverless Framework

3. Create EventBridge rule (hourly trigger)

### Demo Flow

**Minute 1: Show Initial State**
```bash
# Display current product prices
aws s3 cp s3://pricing-demo/products.csv - | column -t -s,

# Show competitor prices
aws s3 cp s3://pricing-demo/competitor_prices.csv - | column -t -s,
```

**Minute 2: Simulate Competitor Price Drop**
```bash
# Update competitor_prices.csv - drop Competitor A price for P001 from 950 to 850
# Upload to S3
aws s3 cp competitor_prices_updated.csv s3://pricing-demo/competitor_prices.csv
```

**Minute 3: Trigger Price Monitor (Manual)**
```bash
# Invoke Price Monitor Lambda
aws lambda invoke --function-name PriceMonitor response.json

# Show detection
cat response.json
# Output: {"detected_changes": [{"product_id": "P001", "competitor_drop": 15.0}]}
```

**Minute 4: Show Autonomous Decision**
```bash
# Check decision log
aws s3 ls s3://pricing-demo/decisions/

# Download latest decision
aws s3 cp s3://pricing-demo/decisions/D_20240227_140530_P001.json - | jq .

# Output shows:
# - Old price: 1000
# - New price: 925
# - Reasoning: "Competitor dropped 15% to ₹850. Matching 50% of drop..."
# - Guardrail: pass
# - Executed: true
```

**Minute 5: Verify Price Update**
```bash
# Show updated products.csv
aws s3 cp s3://pricing-demo/products.csv - | grep P001

# Output: P001,Wireless Mouse,Electronics,600,925,30,2024-02-27T14:06:00Z
```

### Key Demo Points

✅ **Autonomous**: No human approval needed  
✅ **Fast**: Detection to execution in <2 minutes  
✅ **Safe**: Guardrail protected minimum margin  
✅ **Auditable**: Complete decision log with reasoning  
✅ **Scalable**: Handles all 10 products simultaneously

## 9. Implementation Timeline (4-5 Days)

### Day 1 (Feb 27): Setup & Data Preparation
- [ ] Create AWS account and configure credentials
- [ ] Set up S3 bucket structure
- [ ] Create sample data files (products.csv, competitor_prices.csv, config.json)
- [ ] Write data generation script for competitor price variations
- [ ] Test S3 uploads and downloads

**Deliverable**: S3 bucket with sample data

### Day 2 (Feb 28): Price Monitor Lambda
- [ ] Create Lambda function skeleton (Python 3.11)
- [ ] Implement CSV reading from S3
- [ ] Write price comparison logic (detect >5% changes)
- [ ] Add CloudWatch logging
- [ ] Test with sample data

**Deliverable**: Working Price Monitor Lambda

### Day 3 (Mar 1): Price Decision Engine Lambda
- [ ] Create Decision Engine Lambda
- [ ] Implement rule-based pricing algorithm
- [ ] Add minimum margin guardrail check
- [ ] Generate decision JSON with reasoning
- [ ] Write decision logs to S3
- [ ] Test with various scenarios

**Deliverable**: Working Decision Engine Lambda

### Day 4 (Mar 2): Price Executor & Integration
- [ ] Create Price Executor Lambda
- [ ] Implement CSV update logic
- [ ] Add execution logging
- [ ] Create EventBridge rule (hourly trigger)
- [ ] Wire all 3 Lambdas together
- [ ] End-to-end testing

**Deliverable**: Complete autonomous pricing system

### Day 5 (Mar 3): Demo Prep & Documentation
- [ ] Create demo scenario script
- [ ] Write README with setup instructions
- [ ] Create architecture diagram
- [ ] Prepare 5-minute demo walkthrough
- [ ] Test demo flow multiple times
- [ ] Prepare judge Q&A responses

**Deliverable**: Demo-ready system with documentation

### Contingency Buffer

If ahead of schedule:
- Add simple CLI tool to query decision logs
- Create visualization script for price changes over time
- Add email notifications for large price changes

If behind schedule:
- Skip EventBridge, trigger manually for demo
- Simplify decision logging (just essential fields)
- Use hardcoded config instead of config.json

## 10. Technical Stack

### Core Technologies

**Runtime**: Python 3.11
- Simple, fast development
- Great AWS Lambda support
- Rich CSV/JSON libraries (pandas, json)

**AWS Services**:
- Lambda (compute)
- S3 (storage)
- EventBridge (scheduling)
- CloudWatch (logging)
- SAM or Serverless Framework (deployment)

**Libraries**:
```python
# requirements.txt
boto3==1.34.0        # AWS SDK
pandas==2.1.0        # CSV processing
python-dateutil==2.8.2  # Timestamp handling
```

**Development Tools**:
- AWS CLI for testing
- VS Code with AWS Toolkit
- Git for version control

### Project Structure

```
autonomous-pricing-engine/
├── src/
│   ├── price_monitor/
│   │   ├── handler.py          # Lambda entry point
│   │   └── requirements.txt
│   ├── price_decision/
│   │   ├── handler.py          # Decision logic
│   │   ├── pricing_rules.py    # Rule-based algorithm
│   │   └── requirements.txt
│   └── price_executor/
│       ├── handler.py          # Execution logic
│       └── requirements.txt
├── data/
│   ├── products.csv
│   ├── competitor_prices.csv
│   └── config.json
├── template.yaml               # SAM template
├── README.md
└── demo_script.sh             # Demo automation
```

### Deployment

**Option 1: AWS SAM**
```bash
sam build
sam deploy --guided
```

**Option 2: Serverless Framework**
```bash
serverless deploy
```

**Option 3: Manual (for quick testing)**
```bash
# Zip Lambda code
cd src/price_monitor && zip -r ../../monitor.zip .

# Upload to Lambda
aws lambda create-function \
  --function-name PriceMonitor \
  --runtime python3.11 \
  --handler handler.lambda_handler \
  --zip-file fileb://monitor.zip \
  --role arn:aws:iam::ACCOUNT:role/lambda-role
```

## 11. Correctness Properties (Simplified)

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do.*

### Property 1: Margin Protection
*For any* pricing decision, the new price SHALL maintain at least the configured minimum margin percentage above cost.

**Validates: Requirements 3.1**

### Property 2: Price Change Detection
*For any* competitor price change greater than the configured threshold (default 5%), the system SHALL generate a pricing decision.

**Validates: Requirements 1.1, 1.2**

### Property 3: Decision Auditability
*For any* executed price change, there SHALL exist a decision log entry containing the old price, new price, reasoning, and timestamp.

**Validates: Requirements 4.1, 4.2**

### Property 4: Guardrail Enforcement
*For any* pricing decision that violates minimum margin constraints, the system SHALL either adjust the price to meet constraints or reject the decision.

**Validates: Requirements 3.1**

### Property 5: Execution Consistency
*For any* approved pricing decision, the product catalog SHALL be updated to reflect the new price within the same execution cycle.

**Validates: Requirements 2.1, 2.2**

## 12. Testing Strategy

### Unit Tests

Test individual components in isolation:

**Price Monitor Tests**:
- Test CSV parsing from S3
- Test price change detection logic
- Test threshold calculations (5% change)
- Test edge cases (missing data, malformed CSV)

**Decision Engine Tests**:
- Test rule-based pricing algorithm
- Test margin guardrail enforcement
- Test decision log generation
- Test various competitor price scenarios

**Price Executor Tests**:
- Test CSV update logic
- Test execution logging
- Test error handling (S3 failures)

### Property-Based Tests

Validate universal properties across many inputs:

**Property Test 1: Margin Protection**
```python
@given(cost=floats(min_value=100, max_value=10000),
       competitor_price=floats(min_value=100, max_value=10000),
       min_margin_pct=floats(min_value=20, max_value=50))
def test_margin_always_protected(cost, competitor_price, min_margin_pct):
    decision = calculate_new_price(cost, competitor_price, min_margin_pct)
    actual_margin = (decision['new_price'] - cost) / cost * 100
    assert actual_margin >= min_margin_pct
```

**Property Test 2: Decision Auditability**
```python
@given(product=products(), competitor_prices=lists(floats()))
def test_all_decisions_logged(product, competitor_prices):
    decision = make_pricing_decision(product, competitor_prices)
    if decision['action'] == 'price_change':
        log_entry = get_decision_log(decision['decision_id'])
        assert log_entry is not None
        assert 'reasoning' in log_entry
        assert 'timestamp' in log_entry
```

### Integration Tests

Test end-to-end flows:

**Test 1: Complete Pricing Cycle**
1. Upload competitor prices with significant change
2. Trigger Price Monitor
3. Verify Decision Engine creates decision
4. Verify Price Executor updates product catalog
5. Verify decision log exists in S3

**Test 2: Guardrail Violation**
1. Upload competitor price below cost
2. Trigger pricing cycle
3. Verify decision respects minimum margin
4. Verify price not set below cost + margin

### Test Configuration

- Unit tests: pytest with standard assertions
- Property tests: Hypothesis library, 100 iterations per test
- Integration tests: boto3 mocking with moto library
- CI/CD: GitHub Actions (optional for hackathon)


## 13. Success Criteria for Hackathon

### Must Have (Demo Blockers)
✅ System detects competitor price changes  
✅ System makes autonomous pricing decisions  
✅ System updates product catalog automatically  
✅ Decision logs show reasoning for each change  
✅ Minimum margin guardrail prevents bad decisions  
✅ End-to-end demo runs in <5 minutes  

### Nice to Have (If Time Permits)
⭐ CLI tool to query decision history  
⭐ Simple visualization of price changes  
⭐ Email notification for large price changes  
⭐ Multiple product categories  

### Out of Scope (Future Work)
❌ Self-correction loop  
❌ AI/LLM integration  
❌ Real-time monitoring  
❌ Web dashboard  
❌ Multi-tenant support  

## 14. Judge Presentation Strategy

### Opening (30 seconds)
"We built an autonomous pricing engine that monitors competitor prices and adjusts your prices automatically—without human approval. Think of it as a pricing manager that works 24/7."

### Demo (3 minutes)
1. Show initial product prices
2. Simulate competitor price drop
3. Show system detecting change
4. Show autonomous decision with reasoning
5. Show updated prices
6. Show complete audit trail

### Technical Highlights (1 minute)
- Serverless architecture (scales to zero, costs nothing when idle)
- Rule-based logic (no AI complexity, fully explainable)
- Guardrails prevent bad decisions (margin protection)
- Complete auditability (every decision logged)

### Business Value (1 minute)
- SMEs currently check prices manually (days of delay)
- Our system responds in minutes (autonomous execution)
- Maintains profitability (guardrails protect margins)
- Costs <$10/month to run (serverless = cheap)

### Q&A Prep
**Q: Why not use AI/ML?**  
A: For a 4-day prototype, rule-based logic is simpler, faster to build, and fully explainable. AI can be added later for demand forecasting.

**Q: How does this scale?**  
A: Serverless architecture scales automatically. Each Lambda can process 1000s of products. S3 handles any data volume.

**Q: What about real competitor data?**  
A: Prototype uses CSV files. Production would integrate with web scraping or competitor APIs.

**Q: Security concerns?**  
A: All data in S3 with IAM policies. Lambda functions have minimal permissions. No external API calls.

## 15. Post-Hackathon Roadmap (If We Win)

### Phase 1: Production Hardening (Week 1-2)
- Add DynamoDB for faster queries
- Implement proper error handling
- Add retry logic for Lambda failures
- Set up CloudWatch alarms

### Phase 2: Real Data Integration (Week 3-4)
- Web scraping for competitor prices
- Integration with e-commerce platforms (Shopify, WooCommerce)
- Real product catalog sync

### Phase 3: Enhanced Intelligence (Month 2)
- Add demand forecasting (simple ML)
- Implement self-correction loop
- Add confidence scoring
- A/B testing framework

### Phase 4: User Interface (Month 3)
- Web dashboard for monitoring
- Mobile app for notifications
- Configuration UI for guardrails
- Analytics and reporting

### Phase 5: Scale & Monetize (Month 4+)
- Multi-tenant architecture
- Freemium pricing model
- ONDC integration
- Partner with SME platforms

---

**This design prioritizes working software over comprehensive features. The goal is to demonstrate autonomous pricing execution in 4-5 days with minimal AWS costs.**
