"""
Market Processor Lambda Handler

Processes market data events and updates product information in DynamoDB.
Acts as the entry point for market signals (competitor prices, demand signals).
"""

import json
from typing import Any, Dict
import sys
import os

# Add shared module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


def process_market_data(event: Dict[str, Any]) -> Dict[str, Any]:
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
    - API Gateway
    - EventBridge
    - SQS
    - Direct invocation

    Args:
        event: Lambda event payload
        context: Lambda context

    Returns:
        JSON response with processing result
    """
    logger.info(f"Market processor invoked with event: {json.dumps(event, default=str)}")

    try:
        # Handle different event sources
        if 'Records' in event:
            # SQS or Kinesis batch
            results = []
            for record in event['Records']:
                if 'body' in record:
                    # SQS
                    body = json.loads(record['body'])
                elif 'kinesis' in record:
                    # Kinesis
                    body = json.loads(record['kinesis']['data'])
                else:
                    body = record

                result = process_market_data(body)
                results.append(result)

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'processed': len(results),
                    'results': results
                })
            }

        elif 'detail' in event:
            # EventBridge event
            result = process_market_data(event['detail'])
        else:
            # Direct invocation
            result = process_market_data(event)

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