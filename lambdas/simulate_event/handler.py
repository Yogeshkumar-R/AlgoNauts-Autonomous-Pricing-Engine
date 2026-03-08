"""
Simulate Event Lambda Handler

Generates synthetic market events for hackathon demo.
Picks a random product from DynamoDB, generates competitor price drop
or demand spike scenario, then starts the Step Functions pricing pipeline.

POST /simulate
Body: { "scenario": "competitor_drop" | "demand_spike" | "inventory_shift" | "random" }
"""

import json
import boto3
import os
import sys
import random
from typing import Any, Dict

# Add shared module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    DynamoDBClient,
    setup_logger,
    generate_timestamp,
    PRODUCTS_TABLE,
    STATUS_SUCCESS,
    STATUS_FAILED
)

logger = setup_logger(__name__)
db_client = DynamoDBClient()

_region = os.environ.get('BEDROCK_REGION', os.environ.get('AWS_REGION', 'us-east-1'))
_sf_client = None


def get_sf_client():
    global _sf_client
    if _sf_client is None:
        _sf_client = boto3.client('stepfunctions', region_name=_region)
    return _sf_client


# Scenario definitions
SCENARIOS = {
    'competitor_drop': {
        'description': 'Competitor dropped price by 20-35%',
        'price_factor_range': (0.65, 0.80),   # competitor is 65-80% of our current price
        'demand_factor_range': (0.75, 0.95),   # demand dips when competitor drops price
    },
    'demand_spike': {
        'description': 'Demand spiked due to seasonal/viral trend',
        'price_factor_range': (0.95, 1.10),    # competitor stable
        'demand_factor_range': (1.4, 1.8),     # demand much higher
    },
    'inventory_shift': {
        'description': 'Low inventory forces price increase',
        'price_factor_range': (1.0, 1.15),     # competitor slightly higher
        'demand_factor_range': (1.1, 1.3),     # moderate demand still there
    },
}


def pick_random_product() -> Dict[str, Any]:
    """Fetch all products and return one at random."""
    products = db_client.scan(PRODUCTS_TABLE)
    if not products:
        raise ValueError("No products found in DynamoDB. Run /seed first.")
    return random.choice(products)


def generate_synthetic_event(product: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Generate realistic synthetic market event for the given scenario."""
    if scenario == 'random':
        scenario = random.choice(list(SCENARIOS.keys()))

    cfg = SCENARIOS.get(scenario, SCENARIOS['competitor_drop'])

    current_price = float(product.get('current_price', product.get('cost_price', 500) * 1.3))
    price_factor = random.uniform(*cfg['price_factor_range'])
    competitor_price = round(current_price * price_factor, 2)
    demand_factor = round(random.uniform(*cfg['demand_factor_range']), 2)

    # Update product in DynamoDB with new market conditions
    db_client.update_item(
        PRODUCTS_TABLE,
        {'product_id': product['product_id']},
        'SET competitor_price = :cp, demand_factor = :df, updated_at = :ua',
        {
            ':cp': competitor_price,
            ':df': demand_factor,
            ':ua': generate_timestamp()
        }
    )

    return {
        'product_id': product['product_id'],
        'competitor_price': competitor_price,
        'demand_factor': demand_factor,
        'scenario': scenario,
        'scenario_description': cfg['description'],
        'current_price': current_price,
        'timestamp': generate_timestamp(),
        '_sf_mode': True           # tells each Lambda to return clean JSON (not HTTP response)
    }


def start_pipeline(payload: Dict[str, Any]) -> str:
    """Start the Step Functions pricing pipeline with the generated event."""
    state_machine_arn = os.environ.get('STATE_MACHINE_ARN')
    if not state_machine_arn:
        raise ValueError("STATE_MACHINE_ARN environment variable not set")

    execution_name = f"demo-{payload['product_id']}-{payload['timestamp'].replace(':', '-').replace('.', '-')[:30]}"

    response = get_sf_client().start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=json.dumps(payload)
    )
    return response['executionArn']


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point — triggered via POST /simulate.
    """
    logger.info(f"SimulateEvent invoked: {json.dumps(event, default=str)[:300]}")

    try:
        # Parse body
        body = {}
        if 'body' in event and event['body']:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']

        scenario = body.get('scenario', 'random')
        product_id = body.get('product_id')   # optional — pick specific product
        
        logger.info(f"Received scenario: {scenario}")
        logger.info(f"Request body: {json.dumps(body)}")

        # Get product
        if product_id:
            product = db_client.get_item(PRODUCTS_TABLE, {'product_id': product_id})
            if not product:
                raise ValueError(f"Product {product_id} not found")
        else:
            product = pick_random_product()

        # Generate synthetic market event
        synthetic_event = generate_synthetic_event(product, scenario)

        # Start Step Functions execution
        execution_arn = start_pipeline(synthetic_event)

        result = {
            'status': STATUS_SUCCESS,
            'message': f"Pricing pipeline started for {synthetic_event['product_id']}",
            'execution_arn': execution_arn,
            'product_id': synthetic_event['product_id'],
            'product_name': product.get('name', synthetic_event['product_id']),
            'scenario': synthetic_event['scenario'],
            'scenario_description': synthetic_event['scenario_description'],
            'generated_data': {
                'current_price': synthetic_event['current_price'],
                'competitor_price': synthetic_event['competitor_price'],
                'demand_factor': synthetic_event['demand_factor'],
            },
            'pipeline_stages': [
                'market_processor',
                'pricing_engine',
                'guardrail_executor',
                'monitoring_agent',
                'correction_agent (if deviation detected)'
            ]
        }

        logger.info(f"Pipeline started: {execution_arn}")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=str)
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'status': STATUS_FAILED, 'error': str(e)})
        }
    except Exception as e:
        logger.exception(f"SimulateEvent error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'status': STATUS_FAILED, 'error': str(e)})
        }
