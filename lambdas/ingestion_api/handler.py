"""
Data Ingestion API Lambda Handler

Receives market data from external sources and pushes to SQS for processing.
This is the entry point for competitor prices, demand signals, and market trends.

Supports:
- Webhook calls from competitor monitoring services
- Scheduled ETL jobs
- Manual data submission
"""

import json
import boto3
from typing import Any, Dict
import os
import sys
from datetime import datetime

# Add shared module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import setup_logger, generate_timestamp, STATUS_SUCCESS, STATUS_FAILED

logger = setup_logger(__name__)

# Initialize AWS clients
sqs = boto3.client('sqs')
eventbridge = boto3.client('events')

# Environment variables
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL', '')
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME', 'autonomous-pricing-event-bus')


def validate_market_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate incoming market data.

    Returns:
        (is_valid, error_message)
    """
    required_fields = ['product_id', 'competitor_price', 'demand_factor']

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate types
    try:
        float(data['competitor_price'])
        if float(data['competitor_price']) < 0:
            return False, "competitor_price must be positive"
    except (ValueError, TypeError):
        return False, "competitor_price must be a number"

    try:
        demand = float(data['demand_factor'])
        if not 0.1 <= demand <= 5.0:
            return False, "demand_factor must be between 0.1 and 5.0"
    except (ValueError, TypeError):
        return False, "demand_factor must be a number"

    # Optional fields validation
    if 'market_trend' in data:
        valid_trends = ['rising', 'stable', 'falling', 'volatile']
        if data['market_trend'] not in valid_trends:
            return False, f"market_trend must be one of: {valid_trends}"

    return True, ""


def send_to_sqs(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send validated market data to SQS queue for async processing.
    """
    try:
        message_body = {
            **data,
            'ingestion_timestamp': generate_timestamp(),
            'source': data.get('source', 'api_ingestion')
        }

        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message_body),
            MessageAttributes={
                'product_id': {
                    'StringValue': data['product_id'],
                    'DataType': 'String'
                },
                'source': {
                    'StringValue': data.get('source', 'unknown'),
                    'DataType': 'String'
                }
            }
        )

        return {
            'status': STATUS_SUCCESS,
            'message_id': response['MessageId'],
            'queue': 'sqs'
        }
    except Exception as e:
        logger.exception(f"Failed to send to SQS: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e)
        }


def send_to_eventbridge(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send market data event directly to EventBridge for real-time processing.
    """
    try:
        response = eventbridge.put_events(
            Entries=[
                {
                    'Source': 'autonomous-pricing.ingestion',
                    'DetailType': 'market_data_received',
                    'Detail': json.dumps({
                        **data,
                        'ingestion_timestamp': generate_timestamp()
                    }),
                    'EventBusName': EVENT_BUS_NAME
                }
            ]
        )

        return {
            'status': STATUS_SUCCESS,
            'event_id': response['Entries'][0].get('EventId'),
            'queue': 'eventbridge'
        }
    except Exception as e:
        logger.exception(f"Failed to send to EventBridge: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e)
        }


def process_ingestion(event: Dict[str, Any], use_sqs: bool = True) -> Dict[str, Any]:
    """
    Process incoming market data ingestion request.

    Args:
        event: API Gateway event or direct invocation
        use_sqs: If True, send to SQS. If False, send directly to EventBridge.

    Returns:
        Processing result
    """
    try:
        # Extract body from API Gateway event
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        # Handle batch ingestion
        if 'records' in body:
            # Batch mode - multiple products
            results = []
            for record in body['records']:
                is_valid, error = validate_market_data(record)
                if not is_valid:
                    results.append({
                        'product_id': record.get('product_id', 'unknown'),
                        'status': STATUS_FAILED,
                        'error': error
                    })
                    continue

                if use_sqs and SQS_QUEUE_URL:
                    result = send_to_sqs(record)
                else:
                    result = send_to_eventbridge(record)

                results.append({
                    'product_id': record['product_id'],
                    **result
                })

            successful = sum(1 for r in results if r.get('status') == STATUS_SUCCESS)
            return {
                'statusCode': 200 if successful == len(results) else 207,
                'body': json.dumps({
                    'status': 'batch_processed',
                    'total': len(results),
                    'successful': successful,
                    'failed': len(results) - successful,
                    'results': results
                })
            }

        # Single product ingestion
        is_valid, error = validate_market_data(body)
        if not is_valid:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'status': STATUS_FAILED,
                    'error': error
                })
            }

        if use_sqs and SQS_QUEUE_URL:
            result = send_to_sqs(body)
        else:
            result = send_to_eventbridge(body)

        return {
            'statusCode': 200 if result['status'] == STATUS_SUCCESS else 500,
            'body': json.dumps({
                'status': STATUS_SUCCESS,
                'product_id': body['product_id'],
                'ingestion_method': result.get('queue', 'unknown'),
                'timestamp': generate_timestamp()
            })
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'status': STATUS_FAILED,
                'error': 'Invalid JSON in request body'
            })
        }
    except Exception as e:
        logger.exception(f"Ingestion error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': STATUS_FAILED,
                'error': str(e)
            })
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for data ingestion API.

    API Gateway endpoints:
    - POST /ingest/market-data - Single product market data
    - POST /ingest/batch - Batch ingestion for multiple products

    Request body:
    {
        "product_id": "PROD-001",
        "competitor_price": 299.99,
        "demand_factor": 1.2,
        "market_trend": "rising",
        "source": "competitor_monitor"
    }
    """
    logger.info(f"Ingestion API invoked: {json.dumps(event, default=str)[:500]}")

    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': ''
        }

    # Get query parameters for routing
    query_params = event.get('queryStringParameters') or {}
    use_sqs = query_params.get('mode', 'sqs').lower() != 'direct'

    result = process_ingestion(event, use_sqs=use_sqs)

    # Add CORS headers
    result['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }

    return result