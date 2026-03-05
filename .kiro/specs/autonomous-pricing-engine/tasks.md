# Implementation Plan: Seller-Focused Autonomous Pricing Engine

**Timeline**: 2 days (March 6-7, 2025)  
**Submission**: March 8 afternoon  
**Goal**: Demo seller-focused pricing assistant for Indian SMEs

---

## Day 1: March 6 (Today) - Core Dashboard & Profit Visibility

### Morning (4 hours) - Dashboard & Profit
- [ ] **Task 1.1**: Create profit-first dashboard layout
  - Main dashboard showing top 5 products by profit
  - Display: product name, current profit, profit margin %, recommendation, confidence score
  - Highlight products with profit below 15% in yellow, below 10% in red
  - Show weekly profit trend (up/down vs last week)
  - Show count of products needing attention

- [ ] **Task 1.2**: Add profit calculation display
  - Show current price excluding GST
  - Show price including GST with GST rate clearly labeled
  - Show cost and profit amount with margin percentage
  - Calculate profit: `price - (cost * 1.18) - platform_fees`

- [ ] **Task 1.3**: Add competitor price comparison
  - Add competitor price display for each product
  - Show local market average price
  - Show online platform average price
  - Show lowest and highest competitor prices
  - Show how your price compares to averages (percentage above/below)

- [ ] **Task 1.4**: Implement recommendation display
  - Create recommendation card UI
  - Display one of three actions: Keep, Lower, or Raise
  - Show recommended price if action is not Keep
  - Show expected profit impact as percentage change

**Goal**: Working dashboard showing profit, competitors, recommendations

### Afternoon (5 hours) - Explanations & Trust
- [ ] **Task 2.1**: Build simple explanation generator
  - Generate explanations for Keep recommendations
  - Generate explanations for Lower recommendations
  - Generate explanations for Raise recommendations
  - Use seller-friendly language (avoid technical terms)

- [ ] **Task 2.2**: Add confidence score display
  - Add confidence score to recommendation cards
  - Display score as percentage (0-100%)
  - Show color coding: green (80%+), yellow (70-79%), red (<70%)
  - Show what factors contributed to confidence score

- [ ] **Task 2.3**: Implement GST visibility
  - Implement GST display for all prices
  - Show price excluding GST
  - Show price including GST
  - Display applicable GST rate (5%, 12%, 18%, or 28%)

- [ ] **Task 2.4**: Add festival season awareness
  - Add festival season indicator to dashboard
  - Show active festival season (Diwali, Holi, Eid, etc.)
  - Display festival impact on pricing strategy

**Goal**: Sellers understand why recommendations are made

---

## Day 2: March 7 - Quick Actions & Demo

### Morning (4 hours) - Quick Actions
- [ ] **Task 2.5**: Implement 1-click price adjustment
  - Add "Adjust Price" button to product cards
  - Show confirmation screen with new price, profit impact, explanation
  - Apply change with one click after confirmation
  - Show "Undo Last Change" button for 5 minutes after adjustment

- [ ] **Task 2.6**: Create weekly profit summary
  - Create weekly profit summary view
  - Show current week total profit
  - Show previous week total profit
  - Show change amount and percentage
  - Show which products contributed most to profit changes

- [ ] **Task 2.7**: Prepare demo scenario
  - Create demo product catalog with various profit margins
  - Create demo scenario script
  - Test end-to-end seller workflow

**Goal**: Sellers can adjust prices and see impact

### Afternoon (5 hours) - Polish & Demo
- [ ] Test end-to-end seller workflow
- [ ] Fix any issues
- [ ] Prepare 5-minute demo walkthrough
- [ ] Write Q&A responses
- [ ] Final documentation review

**Goal**: Demo-ready system

---

## What to Show in Demo (5 minutes)

1. **Open dashboard** - Show profit per product
2. **Show recommendation** - "Wireless Mouse: Keep - 85%"
3. **Click "Why?"** - Show simple explanation
4. **Adjust price** - Click "Lower" → one click → price updated
5. **Show weekly report** - "Profit up 12% vs last week"

---

## Success Criteria (2-Day Timeline)

### Must Have (Demo Blockers)
- [ ] Dashboard shows profit per product
- [ ] Competitor comparison visible
- [ ] Recommendations (Keep/Lower/Raise) displayed
- [ ] Simple explanations for recommendations
- [ ] Confidence scores visible
- [ ] GST calculations visible
- [ ] 1-click price adjustment works
- [ ] Weekly profit summary working

### Nice to Have (If Time Permits)
- [ ] Regional price variations
- [ ] Competitor price notifications
- [ ] Advanced festival awareness

---

## Key Messages for Judges

**What it does**: "A pricing assistant that helps small Indian sellers make smarter pricing decisions that maximize profits while staying competitive."

**Why it matters**: "Indian SMEs manually check competitor prices 1-2 times per week. Our system monitors continuously and makes recommendations in minutes."

**Business impact**: "Expected 10-15% profit margin improvement within 30 days. Sellers can check all products in 5 minutes instead of hours."

**Technical differentiator**: "Built on AWS Lambda, Step Functions, and Bedrock. AI provides explanations, but deterministic logic handles 90% of decisions for speed and cost."

---

## What NOT to Show

❌ Lambda functions  
❌ EventBridge rules  
❌ DynamoDB tables  
❌ Pipeline stages  
❌ API endpoints  

**Focus on what sellers see, not how it's built.**

---

## Notes

- Focus on what sellers see, not technical implementation
- Each task delivers visible value to sellers
- Tasks can be completed in any order within each day
- Demo must show complete seller workflow in <5 minutes
- All explanations must be in plain language, no technical jargon
