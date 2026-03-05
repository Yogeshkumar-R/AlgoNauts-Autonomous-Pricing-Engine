# AlgoNauts - Autonomous Pricing Engine for Indian SMEs

**Helping small Indian sellers maximize profits with simple, actionable pricing guidance**

---

## What This Is

A pricing assistant that helps small Indian sellers make smarter pricing decisions that maximize profits while staying competitive.

### What Sellers Get

- **Profit visibility**: See exactly how much money each product makes
- **Competitor awareness**: Know if prices are too high or too low
- **Simple recommendations**: "Keep", "Lower", or "Raise" with clear reasoning
- **GST-aware calculations**: Understands Indian tax structure
- **Festival pricing**: Special guidance during Diwali, Holi, Eid, etc.
- **Quick actions**: Adjust prices in one click

### What Sellers Don't See

- Lambda functions
- EventBridge rules
- DynamoDB tables
- Pipeline stages
- API endpoints

**The technical complexity is hidden. The value is visible.**

---

## Quick Start

### For Sellers

1. Open the dashboard
2. See your products with profit, recommendations, and confidence scores
3. Click "Keep", "Lower", or "Raise" to adjust prices
4. Check weekly profit summary to see impact

### For Developers

See `docs/seller-architecture-diagram.md` for technical details.

---

## Key Features

### Profit-First Dashboard
Every screen starts with profit—not data pipelines, not system status. **Profit**.

### Competitor Comparison
Know your price relative to local markets and online platforms.

### Actionable Recommendations
Simple guidance: "Keep", "Lower", or "Raise" with expected profit impact.

### Simple Explanations
Understand why each recommendation was made in plain language.

### GST Visibility
All calculations include GST (5%, 12%, 18%, or 28%).

### Festival Awareness
Special pricing guidance during Diwali, Holi, Eid, and other festivals.

### Regional Pricing
Support for different markets (local, regional, online).

---

## Business Impact

### For Indian SMEs

**Before**: Manual price checks 1-2 times per week, decision-to-execution time 2-5 days

**After**: Continuous monitoring, decision-to-execution time <1 minute, autonomous execution for 80%+ of decisions

### Expected Results

- 10-15% profit margin improvement within 30 days
- 80%+ of pricing decisions made within 10 minutes
- 90%+ confidence in AI recommendations
- 5 minutes to check all products (vs hours manually)

---

## Tech Stack

- **Backend**: AWS Lambda, Step Functions, EventBridge
- **Database**: Amazon DynamoDB
- **AI**: Amazon Bedrock (Claude Haiku 4.5)
- **Frontend**: Streamlit (dashboard), Next.js (web app)
- **Monitoring**: Amazon CloudWatch, LangSmith

---

## Project Structure

```
.
├── .kiro/specs/          # Spec files (requirements, design, tasks)
├── docs/                 # Documentation
├── lambdas/              # AWS Lambda functions
├── dashboard/            # Streamlit dashboard
├── frontend/             # Next.js web app
└── infrastructure/       # IAM roles and infrastructure
```

---

## Getting Started

### For Sellers

1. Deploy the system (see `docs/DEPLOYMENT_GUIDE.md`)
2. Open the dashboard
3. Seed demo products
4. Start making smarter pricing decisions

### For Developers

1. Review `docs/seller-architecture-diagram.md`
2. Check `lambdas/README.md` for Lambda function details
3. Deploy using SAM: `cd lambdas && sam build && sam deploy --guided`

---

## Success Criteria

### Seller Workflow Success

- [ ] Can check all products in <5 minutes
- [ ] Can adjust prices in <1 minute
- [ ] Understands why each recommendation was made
- [ ] Confident in AI recommendations 80%+ of the time
- [ ] Can explain price changes to customers

### Business Impact Success

- [ ] Average profit margin increases by 10% within 30 days
- [ ] 80%+ of pricing decisions made within 10 minutes
- [ ] Identifies underperforming products within 24 hours
- [ ] Understands festival season impact on pricing
- [ ] Explains regional price variations

---

## License

MIT License - see LICENSE file for details

---

**Built for AWS Hackathon 2025**  
*Helping Indian SMEs compete with platform sellers*
