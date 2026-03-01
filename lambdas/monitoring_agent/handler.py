"""
Monitoring Agent Lambda Handler

Monitors pricing performance by comparing predicted vs actual sales.
Triggers correction events when deviation exceeds threshold.
"""

import json
import boto3
from typing import Any, Dict, Optional
import sys
import os
import random
from datetime import datetime, timedelta

# Add shared module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    DynamoDBClient,
    setup_logger,
    validate_required_fields,
    generate_timestamp,
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    CORRECTIONS_TABLE,
    DEVIATION_THRESHOLD_PERCENT,
    STATUS_SUCCESS,
    STATUS_FAILED,
    STATUS_CORRECTION_TRIGGERED
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


def simulate_actual_sales(
    predicted_sales: int,
    demand_factor: float,
    market_volatility: float = 0.15
) -> int:
    """
    Simulate actual sales for testing/demo purposes.

    In production, this would be replaced with real sales data from
    analytics systems, POS, or sales databases.

    Args:
        predicted_sales: Predicted sales volume
        demand_factor: Demand multiplier used in prediction
        market_volatility: Random variance factor (default 15%)

    Returns:
        Simulated actual sales count
    """
    # Add random variance to simulate market conditions
    variance = random.uniform(-market_volatility, market_volatility)

    # Bias slightly based on demand factor (high demand = better accuracy)
    accuracy_bias = (demand_factor - 1.0) * 0.1

    adjustment = 1.0 + variance + accuracy_bias
    actual_sales = int(predicted_sales * adjustment)

    return max(0, actual_sales)  # Ensure non-negative


def calculate_deviation(
    predicted: float,
    actual: float
) -> Dict[str, float]:
    """
    Calculate deviation between predicted and actual values.

    Args:
        predicted: Predicted value
        actual: Actual value

    Returns:
        Dictionary with deviation metrics
    """
    if predicted == 0:
        deviation_percent = 100.0 if actual > 0 else 0.0
    else:
        deviation_percent = abs((actual - predicted) / predicted) * 100

    deviation_direction = 'over' if actual > predicted else 'under' if actual < predicted else 'exact'

    return {
        'absolute': abs(actual - predicted),
        'percent': round(deviation_percent, 2),
        'direction': deviation_direction
    }


def get_recent_decision(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the most recent pricing decision for a product using GSI.
    """
    try:
        # Use the ProductTimestampIndex GSI for efficient query
        decisions = db_client.query(
            DECISIONS_TABLE,
            key_condition='product_id = :pid',
            expression_values={':pid': product_id},
            index_name='ProductTimestampIndex',
            limit=1
        )

        if not decisions:
            return None

        # GSI with RANGE key on timestamp — returns sorted ascending; take last item
        decisions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return decisions[0]

    except Exception as e:
        logger.error(f"Error fetching decision for {product_id}: {e}")
        return None


def trigger_correction(
    product_id: str,
    decision_id: str,
    deviation_data: Dict[str, Any],
    performance_data: Dict[str, Any],
    publish_event: bool = True
) -> Dict[str, Any]:
    """
    Create correction event for AI analysis.

    Args:
        product_id: Product identifier
        decision_id: Original decision ID
        deviation_data: Deviation metrics
        performance_data: Performance comparison data

    Returns:
        Correction event record
    """
    timestamp = generate_timestamp()
    correction_id = f"correction_{product_id}_{timestamp}".replace(':', '-').replace('.', '-')

    correction_event = {
        'correction_id': correction_id,
        'product_id': product_id,
        'original_decision_id': decision_id,
        'trigger_type': 'deviation_threshold_exceeded',
        'deviation': deviation_data,
        'performance': performance_data,
        'status': 'pending',
        'created_at': timestamp,
        'retry_count': 0
    }

    # Store correction event
    db_client.put_item(CORRECTIONS_TABLE, correction_event)

    logger.info(f"Created correction event {correction_id} for product {product_id}")

    # In Step Functions mode, orchestration already calls correction agent.
    if publish_event:
        try:
            event_bus = os.environ.get('EVENT_BUS_NAME', 'autonomous-pricing-event-bus')
            get_eventbridge().put_events(Entries=[{
                'Source': 'autonomous-pricing.correction',
                'DetailType': 'correction_triggered',
                'Detail': json.dumps(correction_event),
                'EventBusName': event_bus
            }])
            logger.info(f"Fired correction event {correction_id} to EventBridge")
        except Exception as eb_err:
            logger.warning(f"EventBridge publish failed (non-fatal): {eb_err}")

    return correction_event


def run_monitoring(event: Dict[str, Any], trigger_next: bool = True) -> Dict[str, Any]:
    """
    Execute monitoring logic for a product.

    Args:
        event: Monitoring event containing:
            - product_id: Product identifier
            - decision_id: Optional decision ID to monitor
            - actual_sales: Optional actual sales (will simulate if not provided)
            - threshold_percent: Optional deviation threshold override

    Returns:
        Monitoring result with deviation analysis
    """
    try:
        validate_required_fields(event, ['product_id'])

        product_id = event['product_id']
        decision_id = event.get('decision_id')
        provided_actual_sales = event.get('actual_sales')
        threshold_percent = event.get('threshold_percent', DEVIATION_THRESHOLD_PERCENT)

        timestamp = generate_timestamp()

        # Get product data
        product = db_client.get_item(PRODUCTS_TABLE, {'product_id': product_id})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Get decision data
        if decision_id:
            decision = db_client.get_item(DECISIONS_TABLE, {'decision_id': decision_id})
        else:
            decision = get_recent_decision(product_id)

        if not decision:
            raise ValueError(f"No decision found for product {product_id}")

        decision_id = decision['decision_id']

        # Get predicted values from decision
        predicted_sales = decision['output_data']['predicted_sales']
        predicted_margin = decision['output_data']['predicted_margin']
        recommended_price = decision['output_data']['recommended_price']
        demand_factor = decision['input_data'].get('demand_factor', 1.0)

        # Get or simulate actual sales
        if provided_actual_sales is not None:
            actual_sales = int(provided_actual_sales)
        else:
            actual_sales = simulate_actual_sales(predicted_sales, demand_factor)

        # Calculate deviation
        sales_deviation = calculate_deviation(predicted_sales, actual_sales)

        # Calculate actual margin (simulated)
        # In production, this would come from actual financial data
        actual_margin = predicted_margin + random.uniform(-3, 3)
        actual_margin = round(max(0, actual_margin), 2)

        margin_deviation = calculate_deviation(predicted_margin, actual_margin)

        # Prepare performance data
        performance_data = {
            'predicted_sales': predicted_sales,
            'actual_sales': actual_sales,
            'sales_deviation': sales_deviation,
            'predicted_margin': predicted_margin,
            'actual_margin': actual_margin,
            'margin_deviation': margin_deviation,
            'current_price': recommended_price
        }

        # Check if deviation exceeds threshold
        correction_triggered = False
        correction_event = None

        if sales_deviation['percent'] > threshold_percent:
            logger.warning(
                f"Deviation {sales_deviation['percent']}% exceeds threshold "
                f"{threshold_percent}% for product {product_id}"
            )

            correction_event = trigger_correction(
                product_id=product_id,
                decision_id=decision_id,
                deviation_data=sales_deviation,
                performance_data=performance_data,
                publish_event=trigger_next
            )
            correction_triggered = True

        # Update decision with monitoring results
        db_client.update_item(
            DECISIONS_TABLE,
            {'decision_id': decision_id},
            'SET monitored_at = :timestamp, actual_sales = :actual, '
            'actual_margin = :margin, sales_deviation = :deviation',
            {
                ':timestamp': timestamp,
                ':actual': actual_sales,
                ':margin': actual_margin,
                ':deviation': sales_deviation
            }
        )

        logger.info(
            f"Monitoring complete for {product_id}: "
            f"predicted={predicted_sales}, actual={actual_sales}, "
            f"deviation={sales_deviation['percent']}%"
        )

        result = {
            'status': STATUS_SUCCESS,
            'product_id': product_id,
            'decision_id': decision_id,
            'monitoring_timestamp': timestamp,
            'performance': performance_data,
            'threshold_exceeded': correction_triggered,
            'threshold_percent': threshold_percent
        }

        if correction_triggered:
            result['correction_id'] = correction_event['correction_id']
            result['correction_status'] = STATUS_CORRECTION_TRIGGERED

        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }
    except Exception as e:
        logger.exception(f"Error in monitoring agent: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'MONITORING_ERROR'
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for monitoring agent.

    Accepts:
    - Step Functions (_sf_mode: true) — returns clean dict with threshold_exceeded bool
    - EventBridge / Schedule / Direct — returns HTTP response
    """
    logger.info(f"Monitoring agent invoked: {json.dumps(event, default=str)[:300]}")

    sf_mode = bool(event.get('_sf_mode', False))

    # Scheduled trigger — scan products and monitor each
    if event.get('trigger_type') == 'scheduled':
        products = db_client.scan(PRODUCTS_TABLE, limit=50)
        results = []
        for p in (products or []):
            try:
                results.append(run_monitoring({'product_id': p['product_id']}, trigger_next=True))
            except Exception as ex:
                logger.warning(f"Monitoring failed for {p.get('product_id')}: {ex}")
        return {
            'statusCode': 200,
            'body': json.dumps({'monitored': len(results), 'results': results}, default=str)
        }

    try:
        if 'detail' in event:
            detail = event['detail']
            sf_mode = bool(sf_mode or detail.get('_sf_mode', False))
            result = run_monitoring(detail, trigger_next=not sf_mode)
        else:
            result = run_monitoring(event, trigger_next=not sf_mode)

        if sf_mode:
            if result.get('status') == STATUS_FAILED:
                raise Exception(result.get('error', 'monitoring_agent failed'))
            # Ensure threshold_exceeded is a proper bool for Choice state
            result['threshold_exceeded'] = bool(result.get('threshold_exceeded', False))
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
