# Design Document: Seller-Focused Autonomous Pricing Engine

**Target Users**: Indian SME sellers on e-commerce platforms and local markets  
**Budget**: $100 AWS credits  
**Goal**: Help sellers maximize profits with simple, actionable pricing guidance

---

## Seller-Focused Design Philosophy

This is a **pricing assistant**, not a "pricing engine." We're not building internal infrastructure for developers—we're building a tool that helps sellers make more money.

### What Sellers Care About

| Sellers Want | What We Build |
|--------------|---------------|
| "How much profit am I making?" | Profit dashboard per product |
| "Am I priced competitively?" | Competitor price comparison |
| "What should I do?" | Simple recommendations (Keep/Lower/Raise) |
| "Why did this change?" | Plain-language explanations |
| "Am I making the right call?" | Confidence scores (0-100%) |

### What Sellers Don't Care About

❌ Lambda functions  
❌ EventBridge rules  
❌ DynamoDB tables  
❌ Pipeline stages  
❌ API endpoints  

**Our approach**: Build powerful technology behind the scenes, but show sellers only what they need to see.

---

## Core Design Principles

### 1. Profit-First Interface

Every screen starts with profit. Not data pipelines. Not system status. **Profit**.

```
┌─────────────────────────────────────────────────────────────┐
│  Product: Wireless Mouse                                    │
│  Current Price: ₹950 (including 18% GST = ₹1,121)         │
│  Cost: ₹600 + GST                                           │
│  ─────────────────────────────────────────────────────      │
│  Profit: ₹350 (58.3% margin)                                │
│  Competitor Average: ₹920                                   │
│  ─────────────────────────────────────────────────────      │
│  Recommendation: KEEP                                       │
│  Confidence: 85%                                            │
│  Explanation: Your price is already competitive.            │
│              Competitors are averaging ₹920, you're at ₹950.│
└─────────────────────────────────────────────────────────────┘
```

### 2. Actionable, Not Analytical

Sellers don't need data—they need decisions.

**Bad**: "Competitor price dropped 15% in the last 24 hours"  
**Good**: "Lower your price to ₹920 to stay competitive. Expected profit: ₹320 (53.3% margin)"

### 3. Indian Context First

- GST visible in every calculation
- Festival season awareness (Diwali, Holi, Eid)
- Regional market awareness (local vs online)
- Simple rupee amounts (no decimals)

### 4. Trust Through Transparency

Every recommendation includes:
- **What changed**: "Competitor lowered price by ₹50"
- **Why it matters**: "You're now 5% above competitor average"
- **Expected impact**: "Lowering to ₹920 gives ₹320 profit (53.3%)"

---

## Dashboard Design

### Main Dashboard (Overview)

```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 Pricing Dashboard                                               │
│  ─────────────────────────────────────────────────────────────      │
│  📈 Weekly Profit: ₹45,230 (+12% vs last week)                      │
│  ⏰ Last checked: 2 hours ago                                       │
│  ─────────────────────────────────────────────────────────────      │
│  🔔 3 products need attention                                       │
│  ─────────────────────────────────────────────────────────────      │
│                                                                       │
│  Top Products by Profit                                             │
│  ─────────────────────────────────────────────────────────────      │
│                                                                       │
│  🟢 Wireless Mouse                                                  │
│     Profit: ₹350 (58.3%)  │  Recommendation: KEEP  │  Confidence: 85%│
│                                                                       │
│  🟡 USB Keyboard                                                    │
│     Profit: ₹280 (46.7%)  │  Recommendation: LOWER  │  Confidence: 72%│
│                                                                       │
│  🔴 Laptop Stand                                                    │
│     Profit: ₹95 (23.8%)   │  Recommendation: LOWER  │  Confidence: 68%│
│                                                                       │
│  🟢 WebCam HD                                                       │
│     Profit: ₹520 (43.3%)  │  Recommendation: KEEP  │  Confidence: 91%│
│                                                                       │
│  🟢 Phone Case                                                      │
│     Profit: ₹250 (62.5%)  │  Recommendation: RAISE  │  Confidence: 78%│
│                                                                       │
│  [View All Products]  [Quick Adjust]  [Weekly Report]              │
└─────────────────────────────────────────────────────────────────────┘
```

### Product Detail View

```
┌─────────────────────────────────────────────────────────────────────┐
│  📦 Wireless Mouse                                                  │
│  ─────────────────────────────────────────────────────────────      │
│                                                                       │
│  Current Pricing                                                    │
│  ─────────────────────────────────────────────────────────────      │
│  Your Price:        ₹950 (excluding GST)                           │
│  Price with GST:    ₹1,121 (18% GST)                               │
│  Cost:              ₹600 + GST                                     │
│  Profit:            ₹350 (58.3% margin)                            │
│                                                                       │
│  Competitor Comparison                                              │
│  ─────────────────────────────────────────────────────────────      │
│  Local Market Avg:  ₹920 (3 sellers)                               │
│  Online Avg:        ₹940 (5 sellers)                               │
│  Your Position:     3% below local, 1% below online                │
│                                                                       │
│  Recommendation                                                     │
│  ─────────────────────────────────────────────────────────────      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  🟢 KEEP                                                      │  │
│  │  Current price is optimal.                                    │  │
│  │  Confidence: 85%                                              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  Why Keep?                                                          │
│  ─────────────────────────────────────────────────────────────      │
│  Your price (₹950) is already competitive. Competitors are         │
│  averaging ₹920 locally and ₹940 online. Lowering further would    │
│  reduce your profit without significant sales gain.                │
│                                                                       │
│  Expected Impact:                                                   │
│  - If you keep: Profit stays at ₹350 (58.3%)                      │
│  - If you lower to ₹920: Profit drops to ₹320 (53.3%)             │
│  - If you raise to ₹980: Profit increases to ₹380 (60.0%)         │
│                            but may lose 10% of sales                │
│                                                                       │
│  [Adjust Price]  [Undo Last Change]  [More Details]                │
└─────────────────────────────────────────────────────────────────────┘
```

### Weekly Profit Report

```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 Weekly Profit Report                                            │
│  ─────────────────────────────────────────────────────────────      │
│  Week: Feb 24 - Mar 2                                               │
│                                                                       │
│  Profit Summary                                                     │
│  ─────────────────────────────────────────────────────────────      │
│  Current Week:     ₹45,230                                          │
│  Previous Week:    ₹40,350                                          │
│  Change:           +₹4,880 (+12%)                                   │
│                                                                       │
│  Top Profit Drivers                                                 │
│  ─────────────────────────────────────────────────────────────      │
│  1. Wireless Mouse    +₹1,200 (5 price adjustments)                │
│  2. WebCam HD         +₹950 (3 price adjustments)                  │
│  3. Phone Case        +₹780 (2 price adjustments)                  │
│                                                                       │
│  Festival Impact (Holi Season)                                      │
│  ─────────────────────────────────────────────────────────────      │
│  Holi-special products: +₹2,100 profit increase                    │
│  Average margin increase: +4.2%                                    │
│                                                                       │
│  Regional Performance                                               │
│  ─────────────────────────────────────────────────────────────      │
│  Local Market:     ₹18,450 (15% above target)                      │
│  Online Platform:  ₹26,780 (10% above target)                      │
│                                                                       │
│  [Download PDF]  [Share Report]  [Compare Months]                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Seller Workflows

### Daily Price Check Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. Open Dashboard (0 seconds)                                      │
│     └─ See profit overview for all products                         │
│                                                                       │
│  2. Review Red/Yellow Products (2 minutes)                          │
│     └─ Products with <15% profit highlighted                         │
│                                                                       │
│  3. Check Recommendations (1 minute per product)                    │
│     └─ Keep/Lower/Raise with confidence scores                      │
│                                                                       │
│  4. Make Adjustments (30 seconds per change)                        │
│     └─ One-click price adjustment with confirmation                 │
│                                                                       │
│  5. Review Weekly Impact (2 minutes)                                │
│     └─ See how changes affected profit                              │
│                                                                       │
│  Total Time: <5 minutes for all products                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Quick Price Adjustment Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. Find Product in Dashboard                                       │
│                                                                       │
│  2. Click "Adjust Price" Button                                     │
│                                                                       │
│  3. See Recommendation Card                                         │
│     ┌─────────────────────────────────────────────────────────────┐ │
│     │  🟢 LOWER to ₹920                                           │ │
│     │  Expected Profit: ₹320 (53.3%)                              │ │
│     │  Confidence: 72%                                            │ │
│     │                                                              │ │
│     │  Why: Competitors averaging ₹920, you're at ₹950            │ │
│     └─────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  4. Confirm with One Click                                          │
│                                                                       │
│  5. See Updated Dashboard                                           │
│     └─ Profit updated to ₹320, recommendation updated               │
│                                                                       │
│  Total Time: <1 minute                                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Understanding Recommendations Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  Every recommendation includes:                                     │
│                                                                       │
│  1. Action (Keep/Lower/Raise)                                       │
│     └─ Clear, one-word decision                                     │
│                                                                       │
│  2. Confidence Score (0-100%)                                       │
│     └─ 80%+ = Trust the recommendation                             │
│     └─ 70-79% = Review before acting                               │
│     └─ <70% = Consider human judgment                              │
│                                                                       │
│  3. Plain-Language Explanation                                      │
│     └─ What changed, why it matters, expected impact               │
│                                                                       │
│  4. Expected Profit Impact                                          │
│     └─ Show profit before and after proposed change                │
│                                                                       │
│  5. "Why This Matters" Section                                      │
│     └─ Connect to seller's goals (more profit, more sales, etc.)   │
│                                                                       │
│  Sellers can ask "Why?" and get answers in simple terms.            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technical Architecture (Behind the Scenes)

The technical implementation is hidden from sellers. Here's what powers the dashboard:

### System Components

**Data Collection Layer** (Hidden from sellers):
- Competitor price monitoring (hourly checks)
- Platform fee integration (e-commerce marketplaces)
- GST rate database (5%, 12%, 18%, 28%)
- Festival calendar (Diwali, Holi, Eid, etc.)

**Pricing Engine** (Hidden from sellers):
- Profit calculation engine
- Competitor comparison logic
- Recommendation algorithm
- Confidence scoring system

**Data Storage** (Hidden from sellers):
- Product catalog with costs and prices
- Competitor price history
- Decision logs with reasoning
- Profit tracking over time

**API Layer** (Hidden from sellers):
- REST endpoints for dashboard data
- Real-time updates for price changes
- Notification system for competitor moves

### Data Flow (Simplified)

```
Competitor Prices → Data Collector → Pricing Engine → Dashboard
     (Hourly)        (Lambda)         (Lambda)        (API)
                                                    ↓
                                              Seller Sees:
                                              - Profit per product
                                              - Recommendations
                                              - Explanations
```

---

## Data Models (Seller-Focused)

### Product View (What Sellers See)

```json
{
  "product_id": "P001",
  "name": "Wireless Mouse",
  "current_price": 950,
  "price_with_gst": 1121,
  "gst_rate": 18,
  "cost": 600,
  "profit": 350,
  "profit_margin_pct": 58.3,
  "competitor_comparison": {
    "local_market_avg": 920,
    "online_avg": 940,
    "lowest_competitor": 899,
    "highest_competitor": 980
  },
  "recommendation": {
    "action": "KEEP",
    "confidence_pct": 85,
    "explanation": "Your price is already competitive. Competitors are averaging ₹920 locally and ₹940 online. Lowering further would reduce your profit without significant sales gain.",
    "expected_impact": {
      "keep": {"profit": 350, "margin_pct": 58.3},
      "lower_to_920": {"profit": 320, "margin_pct": 53.3},
      "raise_to_980": {"profit": 380, "margin_pct": 60.0, "sales_impact_pct": -10}
    }
  },
  "last_updated": "2024-03-02T10:30:00Z"
}
```

### Recommendation Structure

```json
{
  "action": "KEEP|LOWER|RAISE",
  "recommended_price": 920,
  "confidence_pct": 85,
  "confidence_factors": [
    "Competitor data from 8 sources",
    "Last updated 2 hours ago",
    "Price elasticity is low for this category"
  ],
  "explanation": "Plain language explanation of why this recommendation was made",
  "expected_profit_impact": {
    "current_profit": 350,
    "new_profit": 320,
    "profit_change_pct": -8.6
  },
  "festival_adjustment": {
    "is_active": true,
    "festival": "Holi",
    "seasonal_demand_pct": 15,
    "recommendation_adjustment": "Keep price (demand is high)"
  },
  "regional_adjustment": {
    "market_type": "local",
    "regional_avg": 920,
    "recommendation": "Keep (already below regional average)"
  }
}
```

---

## Success Criteria (Seller-Focused)

### Workflow Success

| Metric | Target | Measurement |
|--------|--------|-------------|
| Check all products | <5 minutes | Timer on dashboard |
| Adjust prices | <1 minute | Time from click to update |
| Understand recommendations | 90%+ | User survey: "Do you understand why?" |
| Trust recommendations | 80%+ | User survey: "Would you follow this?" |
| Profit improvement | 10%+ in 30 days | Compare weekly profit reports |

### Business Impact Success

| Metric | Target | Measurement |
|--------|--------|-------------|
| Average profit margin | 10%+ increase | Weekly profit reports |
| Pricing decisions | 80%+ within 10 min | Dashboard analytics |
| Underperforming products | Identify in <24 hours | Time from low profit to action |
| Festival pricing | 15%+ profit increase | Compare festival vs non-festival |
| Regional optimization | 5%+ margin improvement | Regional profit comparison |

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do.*

### Property 1: Profit Calculation Accuracy
*For any* product, the profit shown to the seller SHALL equal (price - cost - platform fees) × (1 - GST rate/100), with all values clearly labeled.

**Validates: Requirements 1.1, 1.2, 7.5**

### Property 2: Recommendation Consistency
*For any* product with competitor price data, the recommendation (Keep/Lower/Raise) SHALL be consistent with the expected profit impact calculation.

**Validates: Requirements 3.1, 3.2**

### Property 3: Confidence Score Validity
*For any* recommendation, the confidence score (0-100%) SHALL reflect the quality and recency of data used to generate the recommendation.

**Validates: Requirements 6.1, 6.2**

### Property 4: GST Visibility
*For any* product, both the price excluding GST and price including GST SHALL be displayed, with the GST rate clearly labeled.

**Validates: Requirements 7.1, 7.2, 7.4**

### Property 5: Festival Season Awareness
*For any* product during an active festival season, the recommendation SHALL include festival-specific pricing guidance and explain how the festival affects the recommendation.

**Validates: Requirements 8.1, 8.2, 8.3**

### Property 6: Regional Price Accuracy
*For any* product in a specific market (local/online), the competitor comparison SHALL show prices specific to that market type.

**Validates: Requirements 9.1, 9.2, 9.3**

### Property 7: Quick Adjustment Workflow
*For any* price adjustment, the system SHALL complete the change within 1 minute and update the dashboard to reflect the new price and profit.

**Validates: Requirements 10.1, 10.2, 10.3**

### Property 8: Competitor Notification
*For any* competitor price change greater than 5%, the system SHALL notify the seller within 15 minutes with the recommended action.

**Validates: Requirements 11.1, 11.2, 11.3**

### Property 9: Dashboard Overview Accuracy
*For any* dashboard view, the top 5 products by profit SHALL be correctly sorted, and the weekly profit trend SHALL accurately reflect changes from the previous week.

**Validates: Requirements 12.1, 12.2, 12.3**

### Property 10: Undo Functionality
*For any* price adjustment, the system SHALL allow the seller to undo the change within 5 minutes, restoring the previous price and profit calculations.

**Validates: Requirements 10.4**

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:

**Profit Calculation Tests**:
- Test GST-inclusive profit calculations
- Test platform fee deductions
- Test margin percentage calculations
- Test edge cases (zero cost, free products)

**Recommendation Tests**:
- Test Keep/Lower/Raise logic
- Test confidence score generation
- Test explanation generation
- Test festival and regional adjustments

**Dashboard Tests**:
- Test top 5 products sorting
- Test weekly profit trend calculation
- Test notification triggers
- Test real-time updates

### Property-Based Tests

Validate universal properties across many inputs:

**Property Test 1: Profit Calculation**
```python
@given(price=floats(min_value=100, max_value=10000),
       cost=floats(min_value=0, max_value=9999),
       gst_rate=sampled_from([5, 12, 18, 28]),
       platform_fee=floats(min_value=0, max_value=100))
def test_profit_calculation_is_accurate(price, cost, gst_rate, platform_fee):
    profit = calculate_profit(price, cost, gst_rate, platform_fee)
    expected = (price - cost - platform_fee) * (1 - gst_rate / 100)
    assert abs(profit - expected) < 0.01
```

**Property Test 2: Recommendation Consistency**
```python
@given(product=products(), competitor_data=competitor_prices())
def test_recommendation_matches_expected_profit(product, competitor_data):
    recommendation = generate_recommendation(product, competitor_data)
    if recommendation['action'] == 'LOWER':
        assert recommendation['expected_profit_impact']['new_profit'] >= product['profit']
```

### Integration Tests

Test end-to-end seller workflows:

**Test 1: Daily Price Check**
1. Open dashboard
2. Verify all products show profit
3. Verify recommendations are displayed
4. Verify explanations are in plain language
5. Verify confidence scores are present

**Test 2: Quick Price Adjustment**
1. Select a product
2. Click "Adjust Price"
3. Confirm recommendation
4. Verify dashboard updates within 1 minute
5. Verify profit calculation is correct

**Test 3: Festival Season Pricing**
1. Activate festival season
2. Verify dashboard shows festival indicator
3. Verify recommendations include festival guidance
4. Verify profit calculations include festival adjustments

### Test Configuration

- Unit tests: pytest with standard assertions
- Property tests: Hypothesis library, 100 iterations per test
- Integration tests: boto3 mocking with moto library
- CI/CD: GitHub Actions (optional for hackathon)

---

## Implementation Timeline (4-5 Days)

### Day 1 (Feb 27): Dashboard UI & Data Models
- [ ] Create dashboard mockups (profit-first design)
- [ ] Build product view with competitor comparison
- [ ] Implement recommendation card UI
- [ ] Create weekly profit report template
- [ ] Set up data models for seller-facing views

**Deliverable**: Working dashboard UI with seller data

### Day 2 (Feb 28): Profit Calculation Engine
- [ ] Implement profit calculation with GST
- [ ] Add platform fee integration
- [ ] Build competitor comparison logic
- [ ] Create recommendation algorithm
- [ ] Test with sample products

**Deliverable**: Working profit and recommendation engine

### Day 3 (Mar 1): Explanation & Confidence System
- [ ] Build plain-language explanation generator
- [ ] Implement confidence scoring
- [ ] Add festival season awareness
- [ ] Add regional price adjustments
- [ ] Test with various scenarios

**Deliverable**: Complete recommendation system with explanations

### Day 4 (Mar 2): Weekly Reporting & Notifications
- [ ] Build weekly profit report generator
- [ ] Implement competitor price notifications
- [ ] Add undo functionality
- [ ] Create real-time dashboard updates
- [ ] End-to-end testing

**Deliverable**: Complete system with reporting and notifications

### Day 5 (Mar 3): Demo Prep & Documentation
- [ ] Create demo scenario script
- [ ] Write README with setup instructions
- [ ] Prepare seller workflow walkthroughs
- [ ] Test demo flow multiple times
- [ ] Prepare judge Q&A responses

**Deliverable**: Demo-ready system with documentation

---

## Technical Stack

### Core Technologies

**Runtime**: Python 3.11
- Simple, fast development
- Great AWS Lambda support
- Rich data processing libraries

**AWS Services** (Hidden from sellers):
- Lambda (compute)
- S3 (data storage)
- EventBridge (scheduled monitoring)
- CloudWatch (logging)
- API Gateway (dashboard API)

**Libraries**:
```python
# requirements.txt
boto3==1.34.0        # AWS SDK
pandas==2.1.0        # Data processing
python-dateutil==2.8.2  # Date handling
```

### Project Structure

```
autonomous-pricing-engine/
├── src/
│   ├── profit_calculator/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── recommendation_engine/
│   │   ├── handler.py
│   │   ├── explanations.py
│   │   └── requirements.txt
│   └── dashboard_api/
│       ├── handler.py
│       └── requirements.txt
├── data/
│   ├── products.csv
│   ├── competitor_prices.csv
│   └── config.json
├── template.yaml
├── README.md
└── demo_script.sh
```

---

## Post-Hackathon Roadmap

### Phase 1: Production Hardening (Week 1-2)
- Add DynamoDB for faster queries
- Implement proper error handling
- Add retry logic for Lambda failures
- Set up CloudWatch alarms

### Phase 2: Real Data Integration (Week 3-4)
- Web scraping for competitor prices
- Integration with e-commerce platforms
- Real product catalog sync

### Phase 3: Enhanced Intelligence (Month 2)
- Add demand forecasting
- Implement self-correction loop
- Add confidence scoring improvements
- A/B testing framework

### Phase 4: Mobile App (Month 3)
- Mobile app for notifications
- Quick price adjustments on mobile
- Push notifications for competitor changes

### Phase 5: Scale & Monetize (Month 4+)
- Multi-tenant architecture
- Freemium pricing model
- ONDC integration
- Partner with SME platforms

---

**This design prioritizes seller needs over technical complexity. The system works behind the scenes to help sellers make more money, with simple, actionable guidance they can trust.**
