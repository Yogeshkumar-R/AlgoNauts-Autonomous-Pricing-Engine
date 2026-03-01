"""
Market Processor Lambda Handler

Processes market data events and updates product information in DynamoDB.
Acts as the entry point for market signals (competitor prices, demand signals).
"""

import json
import boto3
from typing import Any, Dict
import sys
import os

# Add shared module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    DynamoDBClient,
    setup_logger,
    validate_required_fields,
    generate_timestamp,
    PRODUCTS_TABLE,
    STATUS_SUCCESS,
    STATUS_FAILED
)

logger = setup_logger(__name__)
db_client = DynamoDBClient()

# EventBridge client to trigger next pipeline step
_eventbridge = None

def get_eventbridge():
    global _eventbridge
    if _eventbridge is None:
        _eventbridge = boto3.client('events', region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))
    return _eventbridge


def process_market_data(event: Dict[str, Any], trigger_next: bool = True) -> Dict[str, Any]:
    """
    Process incoming market data and update product records.

    Args:
        event: Market data event containing:
            - product_id: Product identifier
            - competitor_price: Current competitor price
            - demand_factor: Demand multiplier (0.5 - 2.0)
            - market_trend: Optional trend indicator
            - source: Data source identifier

    Returns:
        Processing result with updated product data
    """
    try:
        validate_required_fields(event, ['product_id', 'competitor_price', 'demand_factor'])

        product_id = event['product_id']
        competitor_price = float(event['competitor_price'])
        demand_factor = float(event['demand_factor'])
        market_trend = event.get('market_trend', 'stable')
        source = event.get('source', 'unknown')

        timestamp = generate_timestamp()

        # Fetch existing product data
        product = db_client.get_item(PRODUCTS_TABLE, {'product_id': product_id})

        if not product:
            logger.warning(f"Product {product_id} not found, creating new record")
            product = {
                'product_id': product_id,
                'created_at': timestamp
            }

        # Prepare market data update
        market_data = {
            'competitor_price': competitor_price,
            'demand_factor': demand_factor,
            'market_trend': market_trend,
            'source': source,
            'processed_at': timestamp
        }

        # Update product with new market data
        update_expression = (
            'SET competitor_price = :comp_price, '
            'demand_factor = :demand, '
            'market_trend = :trend, '
            'market_data_source = :source, '
            'market_updated_at = :timestamp, '
            'updated_at = :timestamp'
        )

        expression_values = {
            ':comp_price': competitor_price,
            ':demand': demand_factor,
            ':trend': market_trend,
            ':source': source,
            ':timestamp': timestamp
        }

        # Preserve existing price data
        if 'current_price' in product:
            expression_values[':current_price'] = product['current_price']
            update_expression += ', current_price = :current_price'
        if 'cost_price' in product:
            expression_values[':cost_price'] = product['cost_price']
            update_expression += ', cost_price = :cost_price'
        if 'gst_percent' in product:
            expression_values[':gst_percent'] = product['gst_percent']
            update_expression += ', gst_percent = :gst_percent'

        updated = db_client.update_item(
            PRODUCTS_TABLE,
            {'product_id': product_id},
            update_expression,
            expression_values
        )

        logger.info(f"Processed market data for product {product_id}")

        # In Step Functions mode, orchestration already calls the next stage.
        if trigger_next:
            try:
                event_bus = os.environ.get('EVENT_BUS_NAME', 'autonomous-pricing-event-bus')
                get_eventbridge().put_events(Entries=[{
                    'Source': 'autonomous-pricing.engine',
                    'DetailType': 'price_calculation_requested',
                    'Detail': json.dumps({'product_id': product_id, 'timestamp': timestamp}),
                    'EventBusName': event_bus
                }])
                logger.info(f"Triggered pricing engine for product {product_id}")
            except Exception as eb_err:
                logger.warning(f"EventBridge trigger failed (non-fatal): {eb_err}")

        return {
            'status': STATUS_SUCCESS,
            'product_id': product_id,
            'market_data': market_data,
            'updated_at': timestamp,
            'message': 'Market data processed successfully'
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }
    except Exception as e:
        logger.exception(f"Error processing market data: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'PROCESSING_ERROR'
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for market processor.

    Accepts events from:
    - Step Functions (_sf_mode: true) — returns clean JSON
    - EventBridge (detail key present) — returns HTTP response
    - HTTP API / Direct invocation — returns HTTP response
    """
    logger.info(f"Market processor invoked: {json.dumps(event, default=str)[:300]}")

    try:
        payload = event.get('detail', event)
        sf_mode = bool(event.get('_sf_mode', False) or payload.get('_sf_mode', False))

        if 'detail' in event:
            # EventBridge event
            result = process_market_data(event['detail'], trigger_next=not sf_mode)
        else:
            # Step Functions or direct invocation
            result = process_market_data(event, trigger_next=not sf_mode)

        # Step Functions mode — return clean dict
        if sf_mode:
            if result.get('status') != STATUS_SUCCESS:
                raise Exception(result.get('error', 'market_processor failed'))
            return result

        # HTTP mode
        return {
            'statusCode': 200 if result['status'] == STATUS_SUCCESS else 400,
            'body': json.dumps(result, default=str)
        }

    except Exception as e:
        logger.exception(f"Lambda handler error: {e}")
        if sf_mode:
            raise   # Let Step Functions handle retries/catches
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': STATUS_FAILED,
                'error': str(e),
                'error_type': 'HANDLER_ERROR'
            })
        }
