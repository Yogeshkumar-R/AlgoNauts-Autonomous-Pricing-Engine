# 2-Day Plan for AWS Hackathon (March 6-7, 2025)

**Submission**: March 8 afternoon

## What We're Building

A **pricing assistant** for small Indian sellers that:
- Shows profit per product
- Compares prices to competitors
- Gives simple recommendations (Keep/Lower/Raise)
- Explains why in plain language
- Works in 1-click

## Day 1: March 6 (Today) - Core Dashboard & Profit Visibility

### Morning (4 hours) - Dashboard & Profit
- [ ] Task 1.1: Create profit-first dashboard layout
- [ ] Task 1.2: Add profit calculation display
- [ ] Task 1.3: Add competitor price comparison
- [ ] Task 1.4: Implement recommendation display

**Goal**: Working dashboard showing profit, competitors, recommendations

### Afternoon (5 hours) - Explanations & Trust
- [ ] Task 2.1: Build simple explanation generator
- [ ] Task 2.2: Add confidence score display
- [ ] Task 2.3: Implement GST visibility
- [ ] Task 2.4: Add festival season awareness

**Goal**: Sellers understand why recommendations are made

## Day 2: March 7 - Quick Actions & Demo

### Morning (4 hours) - Quick Actions
- [ ] Task 2.5: Implement 1-click price adjustment
- [ ] Task 2.6: Create weekly profit summary
- [ ] Task 2.7: Prepare demo scenario

**Goal**: Sellers can adjust prices and see impact

### Afternoon (5 hours) - Polish & Demo
- [ ] Test end-to-end seller workflow
- [ ] Fix any issues
- [ ] Prepare 5-minute demo walkthrough
- [ ] Write Q&A responses

**Goal**: Demo-ready system

## What to Show in Demo (5 minutes)

1. **Open dashboard** - Show profit per product
2. **Show recommendation** - "Wireless Mouse: Keep - 85%"
3. **Click "Why?"** - Show simple explanation
4. **Adjust price** - Click "Lower" → one click → price updated
5. **Show weekly report** - "Profit up 12% vs last week"

## Key Messages for Judges

### What It Does
"A pricing assistant that helps small Indian sellers make smarter pricing decisions that maximize profits while staying competitive."

### Why It Matters
"Indian SMEs manually check competitor prices 1-2 times per week. Our system monitors continuously and makes recommendations in minutes."

### Business Impact
"Expected 10-15% profit margin improvement within 30 days. Sellers can check all products in 5 minutes instead of hours."

### Technical Differentiator
"Built on AWS Lambda, Step Functions, and Bedrock. AI provides explanations, but deterministic logic handles 90% of decisions for speed and cost."

## Success Criteria

### Seller Workflow
- [ ] Can check all products in <5 minutes
- [ ] Can adjust prices in <1 minute
- [ ] Understands why each recommendation was made
- [ ] Confident in AI recommendations 80%+ of the time

### Business Impact
- [ ] 10%+ profit margin improvement within 30 days
- [ ] 80%+ of pricing decisions made within 10 minutes
- [ ] Identifies underperforming products within 24 hours

## What NOT to Show

❌ Lambda functions  
❌ EventBridge rules  
❌ DynamoDB tables  
❌ Pipeline stages  
❌ API endpoints  

**Focus on what sellers see, not how it's built.**

## Q&A Prep

**Q: Why not use AI/ML for all decisions?**  
A: For a 2-day prototype, deterministic logic is simpler, faster, and free. AI provides explanations and handles edge cases.

**Q: How does this scale?**  
A: Serverless architecture scales automatically. Each Lambda can process 1000s of products. S3 handles any data volume.

**Q: What about real competitor data?**  
A: Prototype uses CSV files. Production would integrate with web scraping or competitor APIs.

**Q: Security concerns?**  
A: All data in S3 with IAM policies. Lambda functions have minimal permissions. No external API calls.

**Q: How much does it cost?**  
A: Estimated $0-5/month using AWS free tier. Perfect for small sellers.

---

**Remember**: This is a **pricing assistant**, not a "pricing engine." Focus on what sellers experience, not technical architecture.
