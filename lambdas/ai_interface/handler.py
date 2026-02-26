"""
AI Interface Lambda Handler

The "face" of the AI Pricing Manager - provides natural language
interactions, daily summaries, onboarding, and strategic insights.

This is the primary touchpoint for small sellers to interact with
their autonomous pricing system.
"""

import json
from typing import Any, Dict, List, Optional
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

import boto3
from botocore.exceptions import ClientError

# Add shared module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    DynamoDBClient,
    setup_logger,
    validate_required_fields,
    generate_timestamp,
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    CORRECTIONS_TABLE,
    BEDROCK_MODEL_ID,
    BEDROCK_REGION,
    STATUS_SUCCESS,
    STATUS_FAILED
)

logger = setup_logger(__name__)
db_client = DynamoDBClient()

# Initialize Bedrock client (lazy)
_bedrock_client = None


def get_bedrock_client():
    """Get or create Bedrock runtime client."""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=BEDROCK_REGION
        )
    return _bedrock_client


# =============================================================================
# AI PROMPT BUILDERS
# =============================================================================

def build_query_prompt(
    query: str,
    product_data: Optional[Dict],
    decision_data: Optional[Dict],
    seller_context: Dict
) -> str:
    """Build prompt for natural language queries about pricing."""

    product_context = ""
    if product_data:
        product_context = f"""
CURRENT PRODUCT STATE:
- Product ID: {product_data.get('product_id', 'N/A')}
- Current Price: ₹{product_data.get('current_price', 0):.2f}
- Cost Price: ₹{product_data.get('cost_price', 0):.2f}
- Competitor Price: ₹{product_data.get('competitor_price', 0):.2f}
- Demand Factor: {product_data.get('demand_factor', 1.0)}
"""

    decision_context = ""
    if decision_data:
        decision_context = f"""
RECENT PRICING DECISION:
- Recommended Price: ₹{decision_data.get('output_data', {}).get('recommended_price', 0):.2f}
- Predicted Margin: {decision_data.get('output_data', {}).get('predicted_margin', 0):.2f}%
- Predicted Sales: {decision_data.get('output_data', {}).get('predicted_sales', 0)} units
- Strategy: {decision_data.get('pricing_strategy', 'N/A')}
- Status: {decision_data.get('status', 'N/A')}
"""

    prompt = f"""You are an AI Pricing Manager assistant for small sellers. You're helpful, concise, and explain pricing decisions in simple terms that a small business owner would understand.

SELLER CONTEXT:
- Business Name: {seller_context.get('business_name', 'Small Business')}
- Total Products: {seller_context.get('total_products', 0)}
- Average Margin: {seller_context.get('avg_margin', 0):.1f}%
{product_context}
{decision_context}

SELLER QUESTION: "{query}"

Respond in a friendly, conversational tone. Be concise (2-4 sentences). If explaining a price, mention the key factors. If recommending action, be specific. Format prices with ₹ symbol.

Response:"""

    return prompt


def build_daily_summary_prompt(
    seller_id: str,
    products: List[Dict],
    recent_decisions: List[Dict],
    corrections: List[Dict],
    metrics: Dict
) -> str:
    """Build prompt for daily AI summary."""

    # Aggregate insights
    price_increases = sum(1 for d in recent_decisions if d.get('price_change', {}).get('direction') == 'increase')
    price_decreases = sum(1 for d in recent_decisions if d.get('price_change', {}).get('direction') == 'decrease')

    prompt = f"""You are an AI Pricing Manager sending a daily summary to a small seller. Be encouraging, highlight wins, and gently point out opportunities.

TODAY'S METRICS:
- Total Products Managed: {metrics.get('total_products', 0)}
- Pricing Decisions Made: {len(recent_decisions)}
- Prices Increased: {price_increases}
- Prices Decreased: {price_decreases}
- Corrections Applied: {len(corrections)}
- Estimated Daily Profit: ₹{metrics.get('estimated_profit', 0):,.0f}
- Average Margin: {metrics.get('avg_margin', 0):.1f}%

TOP PERFORMERS:
{format_top_performers(products[:3])}

ATTENTION NEEDED:
{format_attention_products(products, corrections)}

Generate a brief, friendly daily summary (3-4 short paragraphs). Start with a greeting. Mention key wins. Highlight 1-2 action items. End with an encouraging note. Use emojis sparingly. Format money as ₹X,XXX.

Daily Summary:"""

    return prompt


def build_onboarding_prompt(
    seller_info: Dict,
    products: List[Dict]
) -> str:
    """Build prompt for AI-powered onboarding recommendations."""

    prompt = f"""You are an AI Pricing Manager helping onboard a new small seller. Analyze their products and provide personalized pricing strategy recommendations.

SELLER INFO:
- Business Name: {seller_info.get('business_name', 'New Seller')}
- Business Type: {seller_info.get('business_type', 'Retail')}
- Experience Level: {seller_info.get('experience', 'Beginner')}

PRODUCTS TO ANALYZE:
{format_products_for_onboarding(products)}

Provide:
1. A warm welcome (1-2 sentences)
2. Overall pricing strategy recommendation for their business type
3. Specific recommendations for 2-3 products (mention product names)
4. 3 quick tips for getting the most from AI pricing

Keep it friendly and actionable. Small business owners should feel confident after reading this.

Onboarding Message:"""

    return prompt


def build_strategy_prompt(
    products: List[Dict],
    decisions: List[Dict],
    market_insights: Dict
) -> str:
    """Build prompt for strategic insights."""

    prompt = f"""You are an AI Pricing Manager providing strategic insights to help a small seller grow their business.

PORTFOLIO OVERVIEW:
- Total Products: {len(products)}
- Average Margin: {sum(p.get('margin', 0) for p in products) / max(len(products), 1):.1f}%
- Products Underperforming: {sum(1 for p in products if p.get('demand_factor', 1) < 0.8)}

MARKET INSIGHTS:
{format_market_insights(market_insights)}

RECENT PRICING PATTERNS:
{format_pricing_patterns(decisions)}

Provide 3-4 strategic recommendations:
1. One immediate opportunity (quick win)
2. One medium-term strategy (this week)
3. One risk to watch
4. One growth opportunity

Be specific with product names and numbers. Small sellers need actionable advice, not generic tips.

Strategic Insights:"""

    return prompt


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_top_performers(products: List[Dict]) -> str:
    """Format top performing products."""
    if not products:
        return "No data yet"

    lines = []
    for p in products:
        name = p.get('product_name', p.get('product_id', 'Unknown'))
        margin = p.get('margin', 0)
        sales = p.get('sales', 0)
        lines.append(f"- {name}: {margin:.1f}% margin, {sales} units sold")
    return "\n".join(lines)


def format_attention_products(products: List[Dict], corrections: List[Dict]) -> str:
    """Format products needing attention."""
    if not corrections:
        return "All products performing normally ✅"

    lines = []
    for c in corrections[:3]:
        pid = c.get('product_id', 'Unknown')
        deviation = c.get('deviation', {}).get('percent', 0)
        lines.append(f"- {pid}: {deviation:.0f}% deviation from prediction")
    return "\n".join(lines)


def format_products_for_onboarding(products: List[Dict]) -> str:
    """Format products for onboarding analysis."""
    if not products:
        return "No products added yet"

    lines = []
    for i, p in enumerate(products[:10], 1):
        name = p.get('product_name', f'Product {i}')
        cost = p.get('cost_price', 0)
        current = p.get('current_price', 0)
        comp = p.get('competitor_price', 'Unknown')
        lines.append(f"{i}. {name}: Cost ₹{cost}, Current ₹{current}, Competitor ₹{comp}")
    return "\n".join(lines)


def format_market_insights(insights: Dict) -> str:
    """Format market insights."""
    return f"""
- Overall Market Trend: {insights.get('trend', 'Stable')}
- Competitive Pressure: {insights.get('competition_level', 'Moderate')}
- Demand Outlook: {insights.get('demand_outlook', 'Normal')}
"""


def format_pricing_patterns(decisions: List[Dict]) -> str:
    """Format pricing patterns from decisions."""
    if not decisions:
        return "Not enough data yet"

    increases = sum(1 for d in decisions if d.get('price_change', {}).get('direction') == 'increase')
    decreases = sum(1 for d in decisions if d.get('price_change', {}).get('direction') == 'decrease')

    return f"""
- Price increases: {increases} products
- Price decreases: {decreases} products
- Most common strategy: {decisions[0].get('pricing_strategy', 'N/A') if decisions else 'N/A'}
"""


def call_bedrock(prompt: str, max_tokens: int = 1000) -> str:
    """Call Bedrock Claude model."""
    try:
        client = get_bedrock_client()

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": 0.7,  # Slightly higher for conversational tone
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        content = response_body.get('content', [])

        if content and len(content) > 0:
            return content[0].get('text', '')

        return "I'm having trouble generating a response. Please try again."

    except ClientError as e:
        logger.error(f"Bedrock API error: {e}")
        return f"I'm having some technical difficulties. Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Unexpected error calling Bedrock: {e}")
        return "Something went wrong. Please try again later."


def get_seller_products(seller_id: str) -> List[Dict]:
    """Get all products for a seller."""
    try:
        # In production, would use GSI on seller_id
        products = db_client.scan(
            PRODUCTS_TABLE,
            filter_expression='seller_id = :sid',
            expression_values={':sid': seller_id}
        )
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return []


def get_recent_decisions(seller_id: str, hours: int = 24) -> List[Dict]:
    """Get recent pricing decisions for a seller."""
    try:
        decisions = db_client.scan(
            DECISIONS_TABLE,
            limit=50
        )
        # Filter by seller's products (simplified)
        return [d for d in decisions if d.get('status') in ['approved', 'completed']][:20]
    except Exception as e:
        logger.error(f"Error fetching decisions: {e}")
        return []


def get_pending_corrections(seller_id: str) -> List[Dict]:
    """Get pending/active corrections for a seller."""
    try:
        corrections = db_client.scan(
            CORRECTIONS_TABLE,
            filter_expression='#status = :status OR #status = :pending',
            expression_values={':status': 'completed', ':pending': 'pending'}
        )
        return corrections[:10]
    except Exception as e:
        logger.error(f"Error fetching corrections: {e}")
        return []


# =============================================================================
# MAIN HANDLERS
# =============================================================================

def handle_natural_language_query(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle natural language queries from sellers about their pricing.

    Event: {
        "query_type": "query",
        "seller_id": "SELLER-001",
        "query": "Why is my iPhone case priced at ₹299?",
        "product_id": "PROD-001" (optional)
    }
    """
    try:
        validate_required_fields(event, ['seller_id', 'query'])

        seller_id = event['seller_id']
        query = event['query']
        product_id = event.get('product_id')

        # Gather context
        product_data = None
        decision_data = None

        if product_id:
            product_data = db_client.get_item(PRODUCTS_TABLE, {'product_id': product_id})
            # Get recent decision for this product
            decisions = db_client.scan(
                DECISIONS_TABLE,
                filter_expression='product_id = :pid',
                expression_values={':pid': product_id},
                limit=1
            )
            if decisions:
                decision_data = decisions[0]

        products = get_seller_products(seller_id)

        seller_context = {
            'business_name': event.get('business_name', 'Your Business'),
            'total_products': len(products),
            'avg_margin': sum(p.get('margin', 10) for p in products) / max(len(products), 1)
        }

        # Build prompt and call AI
        prompt = build_query_prompt(query, product_data, decision_data, seller_context)
        ai_response = call_bedrock(prompt)

        return {
            'status': STATUS_SUCCESS,
            'query': query,
            'response': ai_response,
            'product_id': product_id,
            'timestamp': generate_timestamp()
        }

    except Exception as e:
        logger.exception(f"Error handling query: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e)
        }


def handle_daily_summary(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate daily summary for a seller.

    Event: {
        "query_type": "daily_summary",
        "seller_id": "SELLER-001"
    }
    """
    try:
        validate_required_fields(event, ['seller_id'])
        seller_id = event['seller_id']

        # Gather data
        products = get_seller_products(seller_id)
        decisions = get_recent_decisions(seller_id, hours=24)
        corrections = get_pending_corrections(seller_id)

        # Calculate metrics
        metrics = {
            'total_products': len(products),
            'estimated_profit': sum(p.get('sales', 0) * p.get('margin', 0) / 100 * p.get('current_price', 0) for p in products),
            'avg_margin': sum(p.get('margin', 10) for p in products) / max(len(products), 1)
        }

        # Build prompt and call AI
        prompt = build_daily_summary_prompt(seller_id, products, decisions, corrections, metrics)
        ai_response = call_bedrock(prompt, max_tokens=800)

        return {
            'status': STATUS_SUCCESS,
            'summary': ai_response,
            'metrics': metrics,
            'timestamp': generate_timestamp()
        }

    except Exception as e:
        logger.exception(f"Error generating daily summary: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e)
        }


def handle_onboarding(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle AI-powered onboarding for new sellers.

    Event: {
        "query_type": "onboarding",
        "seller_id": "SELLER-001",
        "seller_info": {
            "business_name": "My Shop",
            "business_type": "Electronics Retail",
            "experience": "Beginner"
        },
        "products": [...] (optional, if already added)
    }
    """
    try:
        validate_required_fields(event, ['seller_id', 'seller_info'])

        seller_id = event['seller_id']
        seller_info = event['seller_info']
        products = event.get('products', [])

        # If no products provided, try to fetch
        if not products:
            products = get_seller_products(seller_id)

        # Build prompt and call AI
        prompt = build_onboarding_prompt(seller_info, products)
        ai_response = call_bedrock(prompt, max_tokens=1200)

        # Store onboarding completion
        timestamp = generate_timestamp()

        return {
            'status': STATUS_SUCCESS,
            'welcome_message': ai_response,
            'seller_id': seller_id,
            'products_analyzed': len(products),
            'timestamp': timestamp,
            'next_steps': [
                "Add your product costs for accurate pricing",
                "Set up competitor tracking",
                "Review AI recommendations weekly"
            ]
        }

    except Exception as e:
        logger.exception(f"Error in onboarding: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e)
        }


def handle_strategy_insights(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate strategic insights for seller's business.

    Event: {
        "query_type": "strategy",
        "seller_id": "SELLER-001",
        "timeframe": "week" (optional)
    }
    """
    try:
        validate_required_fields(event, ['seller_id'])

        seller_id = event['seller_id']
        timeframe = event.get('timeframe', 'week')

        # Gather data
        products = get_seller_products(seller_id)
        decisions = get_recent_decisions(seller_id, hours=168 if timeframe == 'week' else 24)

        # Simulate market insights (would come from market_processor in production)
        market_insights = {
            'trend': 'Stable with slight upward momentum',
            'competition_level': 'Moderate - 2 competitors active in your categories',
            'demand_outlook': 'Normal - holiday season approaching'
        }

        # Build prompt and call AI
        prompt = build_strategy_prompt(products, decisions, market_insights)
        ai_response = call_bedrock(prompt, max_tokens=1000)

        return {
            'status': STATUS_SUCCESS,
            'insights': ai_response,
            'timeframe': timeframe,
            'products_analyzed': len(products),
            'timestamp': generate_timestamp()
        }

    except Exception as e:
        logger.exception(f"Error generating strategy: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e)
        }


def handle_bulk_explanation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate explanations for multiple pricing decisions at once.
    Optimized: 1 LLM call for up to 10 decisions.

    Event: {
        "query_type": "bulk_explanation",
        "seller_id": "SELLER-001",
        "decision_ids": ["decision_1", "decision_2", ...]
    }
    """
    try:
        validate_required_fields(event, ['seller_id', 'decision_ids'])

        seller_id = event['seller_id']
        decision_ids = event['decision_ids'][:10]  # Max 10 at a time

        # Fetch decisions
        decisions_data = []
        for did in decision_ids:
            decision = db_client.get_item(DECISIONS_TABLE, {'decision_id': did})
            if decision:
                decisions_data.append(decision)

        if not decisions_data:
            return {
                'status': STATUS_FAILED,
                'error': 'No valid decisions found'
            }

        # Build batch prompt
        prompt = f"""You are an AI Pricing Manager. Explain these recent pricing decisions in simple terms for a small business owner.

PRICING DECISIONS:
{json.dumps([{
    'product': d.get('product_id'),
    'old_price': d.get('input_data', {}).get('current_price'),
    'new_price': d.get('output_data', {}).get('recommended_price'),
    'reason': d.get('pricing_strategy')
} for d in decisions_data], indent=2)}

Provide a brief 1-2 sentence explanation for each decision. Format as a numbered list. Use ₹ for prices.

Explanations:"""

        ai_response = call_bedrock(prompt, max_tokens=800)

        return {
            'status': STATUS_SUCCESS,
            'explanations': ai_response,
            'decisions_explained': len(decisions_data),
            'timestamp': generate_timestamp()
        }

    except Exception as e:
        logger.exception(f"Error in bulk explanation: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e)
        }


# =============================================================================
# LAMBDA ENTRY POINT
# =============================================================================

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for AI Interface.

    Routes requests based on query_type:
    - query: Natural language questions
    - daily_summary: Daily AI summary
    - onboarding: New seller onboarding
    - strategy: Strategic insights
    - bulk_explanation: Batch explanations
    """
    logger.info(f"AI Interface invoked with event: {json.dumps(event, default=str)}")

    try:
        query_type = event.get('query_type', 'query')

        # Route to appropriate handler
        handlers = {
            'query': handle_natural_language_query,
            'daily_summary': handle_daily_summary,
            'onboarding': handle_onboarding,
            'strategy': handle_strategy_insights,
            'bulk_explanation': handle_bulk_explanation
        }

        handler = handlers.get(query_type)

        if not handler:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'status': STATUS_FAILED,
                    'error': f"Unknown query_type: {query_type}. Valid types: {list(handlers.keys())}"
                })
            }

        result = handler(event)

        return {
            'statusCode': 200 if result['status'] == STATUS_SUCCESS else 400,
            'body': json.dumps(result, default=str)
        }

    except Exception as e:
        logger.exception(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': STATUS_FAILED,
                'error': str(e),
                'error_type': 'HANDLER_ERROR'
            })
        }