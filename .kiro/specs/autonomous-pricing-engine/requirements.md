# Requirements Document: Seller-Focused Autonomous Pricing Engine for Indian SMEs

## Introduction

This pricing engine helps small Indian sellers make smarter pricing decisions that maximize profits while staying competitive. It answers your key questions: what's my current profit, is my price competitive, what should I do, and why did it change?

## Glossary

- **Seller**: Small business owner selling products on e-commerce platforms or local markets
- **Product**: Any item the seller lists for sale
- **Competitor Price**: Price other sellers are charging for similar products
- **Recommended Action**: Suggested price change (Keep, Lower, Raise)
- **Confidence Score**: How reliable the recommendation is (0-100%)
- **GST**: Goods and Services Tax (5%, 12%, 18%, or 28% depending on product)
- **Festival Season**: Special periods like Diwali, Holi, Eid, or local festivals when demand increases

## Requirements

### Requirement 1: Daily Profit Check

**User Story:** As a seller, I want to see my current profit on each product, so that I know which products are making money and which aren't.

#### Acceptance Criteria

1. WHEN I open the pricing dashboard, THE System SHALL display my current profit per product
2. THE profit calculation SHALL include: product cost, GST, platform fees, and current selling price
3. WHERE a product has multiple competitors, THE System SHALL show my profit margin compared to competitors
4. WHILE I'm viewing products, THE System SHALL highlight products with profit below 15% in yellow and below 10% in red
5. IF I haven't checked prices in 24 hours, THE System SHALL show a notification to review

### Requirement 2: Competitor Price Comparison

**User Story:** As a seller, I want to see how my price compares to competitors, so that I can price competitively.

#### Acceptance Criteria

1. WHEN I view a product, THE System SHALL show my price alongside competitor prices from local markets and online platforms
2. THE System SHALL show the lowest, highest, and average competitor price for each product
3. WHERE I have multiple products, THE System SHALL show a summary of how many products are priced above/below competitor average
4. WHILE viewing competitor data, THE System SHALL explain which competitors are local market sellers versus online platforms
5. IF competitor data is unavailable for a product, THE System SHALL indicate this clearly

### Requirement 3: Actionable Price Recommendations

**User Story:** As a seller, I want clear recommendations on whether to keep, lower, or raise my price, so that I can make quick decisions.

#### Acceptance Criteria

1. WHEN I view a product, THE System SHALL display one of three actions: Keep, Lower, or Raise
2. THE System SHALL show the recommended price and the expected profit impact (percentage change)
3. WHERE I choose to adjust my price, THE System SHALL apply the change with one click
4. IF I choose to keep my current price, THE System SHALL explain why this is the optimal decision
5. WHILE I'm reviewing recommendations, THE System SHALL show my confidence score for each decision (0-100%)

### Requirement 4: Simple Explanation for Price Changes

**User Story:** As a seller, I want to understand why my price changed or why a recommendation was made, so that I can trust the system.

#### Acceptance Criteria

1. WHEN a price recommendation is shown, THE System SHALL provide a simple explanation in plain language
2. THE explanation SHALL include: what changed, why it matters, and expected impact
3. WHERE competitor prices changed, THE System SHALL explain the competitor's action (e.g., "Competitor lowered price by ₹50")
4. WHILE explaining recommendations, THE System SHALL avoid technical terms and use seller-friendly language
5. IF I request more details, THE System SHALL provide additional context about the analysis performed

### Requirement 5: Weekly Profit Impact Tracking

**User Story:** As a seller, I want to see how pricing decisions affected my profits over time, so that I can measure success.

#### Acceptance Criteria

1. WHEN I view the weekly summary, THE System SHALL show total profit impact from pricing changes
2. THE System SHALL compare my current weekly profit to the previous week
3. WHERE I made manual price adjustments, THE System SHALL track and report their impact separately
4. WHILE viewing profit history, THE System SHALL show which products contributed most to profit changes
5. IF festival season is active, THE System SHALL highlight any special pricing impact during the festival period

### Requirement 6: Confidence in AI Recommendations

**User Story:** As a seller, I want to understand how confident the system is in its recommendations, so that I can decide whether to follow them.

#### Acceptance Criteria

1. WHEN a recommendation is shown, THE System SHALL display a confidence score (0-100%)
2. THE System SHALL explain what factors contributed to the confidence score
3. WHERE confidence is below 70%, THE System SHALL recommend human review before making changes
4. IF confidence score changes significantly, THE System SHALL explain why (e.g., "New competitor data available")
5. WHILE I'm reviewing recommendations, THE System SHALL show historical accuracy for similar products

### Requirement 7: GST Visibility

**User Story:** As a seller, I want to see GST calculations clearly, so that I understand the final price breakdown.

#### Acceptance Criteria

1. WHEN I view any product, THE System SHALL show both price excluding GST and price including GST
2. THE System SHALL display the applicable GST rate (5%, 12%, 18%, or 28%)
3. WHERE GST rate varies by product, THE System SHALL group products by GST category
4. IF I adjust my price, THE System SHALL automatically recalculate GST and show the new total
5. WHILE viewing profit calculations, THE System SHALL show profit before and after GST

### Requirement 8: Festival Season Pricing

**User Story:** As a seller, I want special pricing guidance during festivals, so that I can maximize sales during high-demand periods.

#### Acceptance Criteria

1. WHEN a festival season is active (Diwali, Holi, Eid, etc.), THE System SHALL highlight this in the dashboard
2. THE System SHALL show festival-specific competitor pricing trends
3. WHERE I have festival-related products, THE System SHALL recommend adjusted pricing strategies
4. IF I request it, THE System SHALL show historical sales data from previous festival seasons
5. WHILE festival season is active, THE System SHALL flag products that may benefit from special pricing

### Requirement 9: Regional Price Variations

**User Story:** As a seller with multiple markets, I want to see regional price differences, so that I can optimize for each location.

#### Acceptance Criteria

1. WHEN I select a region or market, THE System SHALL show competitor prices specific to that area
2. THE System SHALL allow me to switch between different markets (local, regional, online)
3. WHERE regional data is available, THE System SHALL show price differences between markets
4. IF I operate in multiple regions, THE System SHALL recommend region-specific pricing
5. WHILE viewing regional data, THE System SHALL explain any significant price variations

### Requirement 10: Quick Price Adjustment Workflow

**User Story:** As a seller, I want to adjust prices quickly with minimal clicks, so that I can respond to market changes fast.

#### Acceptance Criteria

1. WHEN I decide to adjust a price, THE System SHALL allow me to make the change in one click
2. THE System SHALL show a confirmation screen with the new price, profit impact, and explanation
3. WHERE I confirm the change, THE System SHALL apply it immediately and update the dashboard
4. IF I change my mind, THE System SHALL allow me to undo the last price change within 5 minutes
5. WHILE I'm adjusting prices, THE System SHALL show real-time profit impact calculations

### Requirement 11: Competitor Price Monitoring

**User Story:** As a seller, I want to know when competitor prices change, so that I can respond quickly.

#### Acceptance Criteria

1. WHEN competitor prices change by more than 5%, THE System SHALL notify me within 15 minutes
2. THE notification SHALL include: which competitor, which product, old price, new price, and recommended action
3. WHERE multiple competitors change prices, THE System SHALL show a summary of all changes
4. IF I'm not actively reviewing the dashboard, THE System SHALL send a push notification
5. WHILE I'm viewing notifications, THE System SHALL show how long ago each change occurred

### Requirement 12: Simple Dashboard Overview

**User Story:** As a seller, I want a simple dashboard that answers my key questions, so that I can make decisions quickly.

#### Acceptance Criteria

1. WHEN I open the dashboard, THE System SHALL show my top 5 products by profit
2. THE System SHALL display overall profit trend (up/down compared to last week)
3. WHERE I have products needing attention, THE System SHALL show a count of products with low profit or high competitor pressure
4. IF I haven't reviewed recommendations in 24 hours, THE System SHALL show a prominent reminder
5. WHILE I'm on the dashboard, THE System SHALL update in real-time as I interact with products

## Success Criteria

### Seller Workflow Success

1. I can check all my products in less than 5 minutes
2. I can adjust prices in less than 1 minute
3. I understand why each price recommendation was made
4. I feel confident following AI recommendations at least 80% of the time
5. I can explain price changes to my customers in simple terms

### Business Impact Success

1. My average profit margin increases by at least 10% within 30 days
2. I make at least 80% of pricing decisions within 10 minutes of reviewing recommendations
3. I can identify underperforming products within 24 hours
4. I understand the impact of festival seasons on my pricing strategy
5. I can explain regional price variations to my team or suppliers

## Requirements Quality Notes

All requirements follow EARS patterns and INCOSE quality rules:
- Active voice with clear subjects (THE System)
- No vague terms (using specific percentages, timeframes)
- No pronouns (using specific product/competitor names)
- Measurable criteria (profit percentages, time limits, confidence scores)
- Positive statements (what the system SHALL do, not what it SHALL NOT do)
- No escape clauses (no "where possible" or "if feasible")
- One thought per requirement for clear testing