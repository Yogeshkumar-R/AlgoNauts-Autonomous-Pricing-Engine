"""
Pricing Engine Lambda Handler

Implements deterministic pricing logic to calculate recommended prices
based on cost, competition, demand, and margin requirements.
"""

import json
import boto3
from typing import Any, Dict
import sys
import os
import math
from botocore.exceptions import ClientError

# Add shared module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    DynamoDBClient,
    setup_logger,
    validate_required_fields,
    generate_timestamp,
    generate_decision_id,
    safe_float,
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    MIN_MARGIN_PERCENT,
    STATUS_SUCCESS,
    STATUS_FAILED
)

logger = setup_logger(__name__)
db_client = DynamoDBClient()

# EventBridge client (lazy init)
_eventbridge = None

def get_eventbridge():
    global _eventbridge
    if _eventbridge is None:
        _eventbridge = boto3.client('events', region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))
    return _eventbridge


def calculate_recommended_price(
    cost_price: float,
    competitor_price: float,
    demand_factor: float,
    gst_percent: float,
    min_margin_percent: float = MIN_MARGIN_PERCENT
) -> Dict[str, Any]:
    """
    Calculate recommended price using deterministic pricing logic.

    Pricing Strategy:
    1. Calculate cost with GST: cost_with_gst = cost_price * (1 + gst_percent/100)
    2. Calculate minimum viable price: min_price = cost_with_gst * (1 + min_margin_percent/100)
    3. Adjust for demand: demand_adjusted_price = min_price * demand_factor
    4. Competitor positioning: If competitor_price is viable, position slightly below
    5. Final price: Max of demand_adjusted_price and viable competitor position

    Args:
        cost_price: Product cost price
        competitor_price: Current competitor price
        demand_factor: Demand multiplier (0.5 - 2.0)
        gst_percent: GST percentage
        min_margin_percent: Minimum required margin percentage

    Returns:
        Dictionary with recommended_price and calculation details
    """
    # Step 1: Calculate cost with GST
    cost_with_gst = cost_price * (1 + gst_percent / 100)

    # Step 2: Calculate minimum viable price (ensures minimum margin)
    min_viable_price = cost_with_gst * (1 + min_margin_percent / 100)

    # Step 3: Demand-adjusted base price
    demand_adjusted_price = min_viable_price * demand_factor

    # Step 4: Competitor positioning strategy
    # If competitor price allows margin, position slightly below (2% discount)
    competitor_viable_price = competitor_price * 0.98  # 2% below competitor

    # Ensure competitor-based price still meets margin requirements
    if competitor_viable_price < min_viable_price:
        competitor_viable_price = min_viable_price
        competitor_position = 'above_competitor'  # Cannot beat competitor price profitably
    else:
        competitor_position = 'below_competitor'

    # Step 5: Final recommended price
    # Balance between demand optimization and competitive positioning
    if demand_factor >= 1.0:
        # High demand: prioritize margin optimization
        recommended_price = max(demand_adjusted_price, min_viable_price)
    else:
        # Low demand: prioritize competitive pricing
        recommended_price = min(competitor_viable_price, demand_adjusted_price)
        recommended_price = max(recommended_price, min_viable_price)

    # Round to 2 decimal places
    recommended_price = round(recommended_price, 2)

    # Calculate predicted metrics
    predicted_margin = ((recommended_price - cost_with_gst) / recommended_price) * 100
    predicted_margin = round(predicted_margin, 2)

    # Predicted sales based on demand factor and competitive position
    # Higher demand factor = higher predicted sales
    # Being below competitor = +15% sales boost
    base_sales = 100  # Base unit prediction
    demand_multiplier = demand_factor
    competitive_boost = 1.15 if competitor_position == 'below_competitor' else 0.95
    predicted_sales = int(base_sales * demand_multiplier * competitive_boost)

    return {
        'recommended_price': recommended_price,
        'min_viable_price': round(min_viable_price, 2),
        'cost_with_gst': round(cost_with_gst, 2),
        'predicted_margin': predicted_margin,
        'predicted_sales': predicted_sales,
        'competitor_position': competitor_position,
        'demand_factor': demand_factor,
        'pricing_strategy': 'demand_optimized' if demand_factor >= 1.0 else 'competitive',
        'calculation_details': {
            'raw_demand_adjusted': round(demand_adjusted_price, 2),
            'raw_competitor_price': round(competitor_viable_price, 2),
            'margin_floor_applied': recommended_price == min_viable_price
        }
    }


def run_pricing_engine(event: Dict[str, Any], trigger_next: bool = True) -> Dict[str, Any]:
    """
    Execute pricing engine logic for a product.

    Args:
        event: Pricing event containing:
            - product_id: Product identifier (required)
            - cost_price: Product cost price (optional, uses stored value)
            - current_price: Current selling price (optional)
            - competitor_price: Competitor price (optional, uses stored value)
            - demand_factor: Demand multiplier (optional, uses stored value)
            - gst_percent: GST percentage (optional, uses stored value)

    Returns:
        Pricing decision with recommended price and predictions
    """
    try:
        validate_required_fields(event, ['product_id'])

        product_id = event['product_id']
        timestamp = generate_timestamp()

        # Deterministic idempotency seed:
        # - Step Functions execution id when available
        # - event timestamp for EventBridge style calls
        # - fallback to current timestamp for ad-hoc/manual invokes
        execution_id = str(event.get('_pipeline_execution_id') or '').strip()
        event_timestamp = str(event.get('timestamp') or '').strip()
        if execution_id:
            seed = execution_id.split(':')[-1]
        elif event_timestamp:
            seed = event_timestamp
        else:
            seed = timestamp
        seed = seed.replace(':', '-').replace('.', '-').replace('/', '-')
        decision_id = f"decision_{product_id}_{seed}"

        # Get existing product data
        product = db_client.get_item(PRODUCTS_TABLE, {'product_id': product_id})

        if not product:
            raise ValueError(f"Product {product_id} not found in products table")

        # Merge event data with stored product data
        cost_price = safe_float(event.get('cost_price') or product.get('cost_price'))
        current_price = safe_float(event.get('current_price') or product.get('current_price', 0))
        competitor_price = safe_float(event.get('competitor_price') or product.get('competitor_price', cost_price * 1.2))
        demand_factor = safe_float(event.get('demand_factor') or product.get('demand_factor', 1.0))
        gst_percent = safe_float(event.get('gst_percent') or product.get('gst_percent', 18.0))

        if cost_price == 0:
            raise ValueError("cost_price is required and cannot be zero")

        # Execute pricing calculation
        pricing_result = calculate_recommended_price(
            cost_price=cost_price,
            competitor_price=competitor_price,
            demand_factor=demand_factor,
            gst_percent=gst_percent
        )

        # Calculate price change
        price_change = 0.0
        price_change_percent = 0.0
        if current_price > 0:
            price_change = pricing_result['recommended_price'] - current_price
            price_change_percent = (price_change / current_price) * 100
            price_change_percent = round(price_change_percent, 2)

        # Prepare decision record
        decision = {
            'decision_id': decision_id,
            'product_id': product_id,
            'timestamp': timestamp,
            'input_data': {
                'cost_price': cost_price,
                'current_price': current_price,
                'competitor_price': competitor_price,
                'demand_factor': demand_factor,
                'gst_percent': gst_percent
            },
            'output_data': {
                'recommended_price': pricing_result['recommended_price'],
                'predicted_margin': pricing_result['predicted_margin'],
                'predicted_sales': pricing_result['predicted_sales'],
                'min_viable_price': pricing_result['min_viable_price']
            },
            'price_change': {
                'absolute': round(price_change, 2),
                'percent': price_change_percent,
                'direction': 'increase' if price_change > 0 else 'decrease' if price_change < 0 else 'no_change'
            },
            'pricing_strategy': pricing_result['pricing_strategy'],
            'competitor_position': pricing_result['competitor_position'],
            'status': 'pending_validation',  # Needs guardrail approval
            'created_at': timestamp
        }

        # Store decision in DynamoDB with idempotency guard.
        # If the same decision_id is written twice (retries/duplicate invokes),
        # second write is ignored and treated as success.
        try:
            db_client.put_item(
                DECISIONS_TABLE,
                decision,
                condition_expression='attribute_not_exists(decision_id)'
            )
            logger.info(f"Generated pricing decision {decision_id} for product {product_id}")
        except ClientError as e:
            if e.response.get('Error', {}).get('Code') == 'ConditionalCheckFailedException':
                logger.warning(f"Duplicate pricing decision suppressed for {decision_id}")
                existing = db_client.get_item(DECISIONS_TABLE, {'decision_id': decision_id}) or decision
                decision = existing
                pricing_output = existing.get('output_data', {})
                change_output = existing.get('price_change', {})
                return {
                    'status': STATUS_SUCCESS,
                    'decision_id': decision_id,
                    'product_id': product_id,
                    'recommended_price': pricing_output.get('recommended_price'),
                    'predicted_margin': pricing_output.get('predicted_margin'),
                    'predicted_sales': pricing_output.get('predicted_sales'),
                    'price_change': {
                        'absolute': change_output.get('absolute'),
                        'percent': change_output.get('percent')
                    },
                    'pricing_strategy': existing.get('pricing_strategy'),
                    'next_step': 'Submit to guardrail_executor for validation',
                    'timestamp': existing.get('timestamp', timestamp),
                    'idempotent_reuse': True
                }
            raise

        # In Step Functions mode, orchestration already calls the next stage.
        if trigger_next:
            try:
                event_bus = os.environ.get('EVENT_BUS_NAME', 'autonomous-pricing-event-bus')
                get_eventbridge().put_events(Entries=[{
                    'Source': 'autonomous-pricing.guardrail',
                    'DetailType': 'pricing_decision_ready',
                    'Detail': json.dumps({
                        'decision_id': decision_id,
                        'product_id': product_id,
                        'auto_apply': True
                    }),
                    'EventBusName': event_bus
                }])
                logger.info(f"Triggered guardrail for decision {decision_id}")
            except Exception as eb_err:
                logger.warning(f"EventBridge trigger failed (non-fatal): {eb_err}")

        return {
            'status': STATUS_SUCCESS,
            'decision_id': decision_id,
            'product_id': product_id,
            'recommended_price': pricing_result['recommended_price'],
            'predicted_margin': pricing_result['predicted_margin'],
            'predicted_sales': pricing_result['predicted_sales'],
            'price_change': {
                'absolute': round(price_change, 2),
                'percent': price_change_percent
            },
            'pricing_strategy': pricing_result['pricing_strategy'],
            'next_step': 'Submit to guardrail_executor for validation',
            'timestamp': timestamp
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }
    except Exception as e:
        logger.exception(f"Error in pricing engine: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'PRICING_ERROR'
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for pricing engine.

    Accepts events from:
    - Step Functions (_sf_mode: true) — returns clean dict with decision_id
    - EventBridge (detail key present) — returns HTTP response
    - HTTP API / Direct invocation — returns HTTP response
    """
    logger.info(f"Pricing engine invoked: {json.dumps(event, default=str)[:300]}")

    try:
        sf_mode = bool(event.get('_sf_mode', False))

        if 'Records' in event:
            results = []
            for record in event['Records']:
                body = json.loads(record['body']) if 'body' in record else record
                results.append(run_pricing_engine(body, trigger_next=True))
            return {
                'statusCode': 200,
                'body': json.dumps({'processed': len(results), 'results': results}, default=str)
            }

        elif 'detail' in event:
            detail = event['detail']
            sf_mode = bool(sf_mode or detail.get('_sf_mode', False))
            result = run_pricing_engine(detail, trigger_next=not sf_mode)
        else:
            result = run_pricing_engine(event, trigger_next=not sf_mode)

        # Step Functions mode — return clean dict
        if sf_mode:
            if result.get('status') != STATUS_SUCCESS:
                raise Exception(result.get('error', 'pricing_engine failed'))
            return result

        return {
            'statusCode': 200 if result['status'] == STATUS_SUCCESS else 400,
            'body': json.dumps(result, default=str)
        }

    except Exception as e:
        logger.exception(f"Lambda handler error: {e}")
        if sf_mode:
            raise
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': STATUS_FAILED,
                'error': str(e),
                'error_type': 'HANDLER_ERROR'
            })
        }
