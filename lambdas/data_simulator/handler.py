"""
Market Data Simulator

Simulates realistic market data for testing and demos.
Can be triggered on schedule or on-demand.

This is CRITICAL for the hackathon demo - it generates:
- Competitor price changes
- Demand fluctuations
- Market trend signals
"""

import json
import random
import boto3
from typing import Any, Dict, List
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import setup_logger, generate_timestamp, STATUS_SUCCESS

logger = setup_logger(__name__)

# Initialize AWS clients
eventbridge = boto3.client('events')
dynamodb = boto3.resource('dynamodb')

# Environment variables
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME', 'autonomous-pricing-event-bus')
PRODUCTS_TABLE = os.environ.get('PRODUCTS_TABLE', 'autonomous-pricing-products')

# Sample products for simulation
SAMPLE_PRODUCTS = [
    {
        'product_id': 'PROD-001',
        'name': 'Wireless Bluetooth Earbuds',
        'category': 'Electronics',
        'cost_price': 450.00,  # INR
        'gst_percent': 18,
        'base_price': 899.00,
        'competitor_base': 849.00
    },
    {
        'product_id': 'PROD-002',
        'name': 'Stainless Steel Water Bottle',
        'category': 'Home & Kitchen',
        'cost_price': 180.00,
        'gst_percent': 18,
        'base_price': 399.00,
        'competitor_base': 349.00
    },
    {
        'product_id': 'PROD-003',
        'name': 'USB-C Fast Charging Cable',
        'category': 'Electronics',
        'cost_price': 95.00,
        'gst_percent': 18,
        'base_price': 249.00,
        'competitor_base': 199.00
    },
    {
        'product_id': 'PROD-004',
        'name': 'Yoga Mat Premium',
        'category': 'Sports & Fitness',
        'cost_price': 320.00,
        'gst_percent': 18,
        'base_price': 699.00,
        'competitor_base': 599.00
    },
    {
        'product_id': 'PROD-005',
        'name': 'LED Desk Lamp',
        'category': 'Home & Kitchen',
        'cost_price': 275.00,
        'gst_percent': 18,
        'base_price': 599.00,
        'competitor_base': 549.00
    }
]


def generate_competitor_price(base_price: float, volatility: str = 'normal') -> float:
    """
    Generate a realistic competitor price with random fluctuations.

    Args:
        base_price: Base competitor price
        volatility: 'low', 'normal', 'high', or 'extreme'

    Returns:
        Simulated competitor price
    """
    volatility_factors = {
        'low': 0.02,      # ±2%
        'normal': 0.05,   # ±5%
        'high': 0.10,     # ±10%
        'extreme': 0.20   # ±20%
    }

    factor = volatility_factors.get(volatility, 0.05)
    change = random.uniform(-factor, factor) * base_price

    # Occasionally drop prices significantly (competitor sale)
    if random.random() < 0.1:  # 10% chance
        change = -random.uniform(0.10, 0.25) * base_price  # 10-25% drop
        logger.info(f"Simulating competitor sale: {change/base_price*100:.1f}% price drop")

    return round(base_price + change, 2)


def generate_demand_factor(category: str, market_trend: str) -> float:
    """
    Generate demand factor based on category and market trend.

    Returns:
        Demand multiplier (0.5 - 2.0)
    """
    base_demand = {
        'Electronics': 1.0,
        'Home & Kitchen': 0.9,
        'Sports & Fitness': 0.85
    }

    trend_modifier = {
        'rising': 0.2,
        'stable': 0.0,
        'falling': -0.2,
        'volatile': random.uniform(-0.3, 0.3)
    }

    base = base_demand.get(category, 1.0)
    modifier = trend_modifier.get(market_trend, 0.0)

    # Add random fluctuation
    fluctuation = random.uniform(-0.15, 0.15)

    demand = base + modifier + fluctuation
    return round(max(0.5, min(2.0, demand)), 2)


def generate_market_trend() -> str:
    """Generate a market trend with weighted probabilities."""
    trends = ['rising', 'stable', 'stable', 'stable', 'falling', 'volatile']
    return random.choice(trends)


def initialize_sample_products() -> List[Dict]:
    """
    Initialize sample products in DynamoDB if they don't exist.
    """
    table = dynamodb.Table(PRODUCTS_TABLE)
    initialized = []

    for product in SAMPLE_PRODUCTS:
        try:
            # Check if product exists
            existing = table.get_item(Key={'product_id': product['product_id']})

            if 'Item' not in existing:
                # Create new product
                item = {
                    'product_id': product['product_id'],
                    'name': product['name'],
                    'category': product['category'],
                    'cost_price': product['cost_price'],
                    'gst_percent': product['gst_percent'],
                    'current_price': product['base_price'],
                    'competitor_price': product['competitor_base'],
                    'demand_factor': 1.0,
                    'market_trend': 'stable',
                    'margin_percent': round(
                        ((product['base_price'] - product['cost_price'] * (1 + product['gst_percent']/100))
                         / product['base_price']) * 100, 2
                    ),
                    'created_at': generate_timestamp(),
                    'updated_at': generate_timestamp()
                }
                table.put_item(Item=item)
                initialized.append(product['product_id'])
                logger.info(f"Initialized product: {product['product_id']}")

        except Exception as e:
            logger.error(f"Error initializing product {product['product_id']}: {e}")

    return initialized


def simulate_market_event(product_id: str = None, event_type: str = 'normal') -> Dict[str, Any]:
    """
    Simulate a market event for a single product.

    Args:
        product_id: Specific product ID, or None for random
        event_type: 'normal', 'price_drop', 'demand_surge', 'demand_drop'

    Returns:
        Simulated market data event
    """
    # Select product
    if product_id:
        product = next((p for p in SAMPLE_PRODUCTS if p['product_id'] == product_id), None)
        if not product:
            product = random.choice(SAMPLE_PRODUCTS)
    else:
        product = random.choice(SAMPLE_PRODUCTS)

    # Determine volatility based on event type
    volatility_map = {
        'normal': 'normal',
        'price_drop': 'extreme',
        'demand_surge': 'high',
        'demand_drop': 'high'
    }
    volatility = volatility_map.get(event_type, 'normal')

    # Generate market data
    competitor_price = generate_competitor_price(product['competitor_base'], volatility)
    market_trend = generate_market_trend()

    # Override trend for specific event types
    if event_type == 'demand_surge':
        market_trend = 'rising'
    elif event_type == 'demand_drop':
        market_trend = 'falling'

    demand_factor = generate_demand_factor(product['category'], market_trend)

    event = {
        'product_id': product['product_id'],
        'product_name': product['name'],
        'competitor_price': competitor_price,
        'competitor_change_percent': round(
            ((competitor_price - product['competitor_base']) / product['competitor_base']) * 100, 2
        ),
        'demand_factor': demand_factor,
        'market_trend': market_trend,
        'event_type': event_type,
        'source': 'market_simulator',
        'timestamp': generate_timestamp()
    }

    return event


def send_to_eventbridge(event: Dict[str, Any]) -> bool:
    """Send simulated event to EventBridge."""
    try:
        response = eventbridge.put_events(
            Entries=[
                {
                    'Source': 'autonomous-pricing.simulator',
                    'DetailType': 'market_data_simulated',
                    'Detail': json.dumps(event),
                    'EventBusName': EVENT_BUS_NAME
                }
            ]
        )
        return 'Entries' in response and len(response['Entries']) > 0
    except Exception as e:
        logger.error(f"Failed to send to EventBridge: {e}")
        return False


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point for market data simulator.

    Trigger modes:
    1. Scheduled (EventBridge Schedule) - Simulates market changes
    2. Direct invocation with specific event_type
    3. Batch simulation for multiple products

    Event types:
    - normal: Regular market fluctuation
    - price_drop: Simulate competitor sale/price drop
    - demand_surge: Simulate increased demand
    - demand_drop: Simulate decreased demand
    """
    logger.info(f"Simulator invoked: {json.dumps(event, default=str)[:500]}")

    try:
        # Initialize sample products if needed
        initialized = initialize_sample_products()
        if initialized:
            logger.info(f"Initialized {len(initialized)} sample products")

        # Determine simulation mode
        mode = event.get('mode', 'single')
        event_type = event.get('event_type', 'normal')
        product_id = event.get('product_id')

        results = []

        if mode == 'batch':
            # Simulate for all products
            for product in SAMPLE_PRODUCTS:
                sim_event = simulate_market_event(product['product_id'], event_type)
                sent = send_to_eventbridge(sim_event)
                results.append({
                    'product_id': product['product_id'],
                    'sent': sent,
                    'competitor_price': sim_event['competitor_price'],
                    'demand_factor': sim_event['demand_factor']
                })

        elif mode == 'scenario':
            # Run a predefined scenario (for demos)
            scenarios = event.get('scenarios', [
                {'event_type': 'price_drop', 'delay': 0},
                {'event_type': 'demand_surge', 'delay': 5}
            ])

            for scenario in scenarios:
                sim_event = simulate_market_event(
                    scenario.get('product_id'),
                    scenario.get('event_type', 'normal')
                )
                sent = send_to_eventbridge(sim_event)
                results.append({
                    'scenario': scenario,
                    'event': sim_event,
                    'sent': sent
                })

        else:
            # Single product simulation
            sim_event = simulate_market_event(product_id, event_type)
            sent = send_to_eventbridge(sim_event)
            results.append({
                'product_id': sim_event['product_id'],
                'sent': sent,
                'event': sim_event
            })

        successful = sum(1 for r in results if r.get('sent', False))

        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': STATUS_SUCCESS,
                'mode': mode,
                'total_events': len(results),
                'successful': successful,
                'results': results,
                'timestamp': generate_timestamp()
            })
        }

    except Exception as e:
        logger.exception(f"Simulator error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error': str(e)
            })
        }