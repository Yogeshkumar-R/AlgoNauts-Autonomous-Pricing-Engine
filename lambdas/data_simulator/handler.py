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
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import setup_logger, generate_timestamp, STATUS_SUCCESS

logger = setup_logger(__name__)

# Initialize AWS clients
eventbridge = boto3.client('events')
dynamodb = boto3.resource('dynamodb')

# Environment variables
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME', 'autonomous-pricing-event-bus')
PRODUCTS_TABLE = os.environ.get('PRODUCTS_TABLE', 'autonomous-pricing-products')

# Sample products for simulation - Chennai Mobile Shop inventory
SAMPLE_PRODUCTS = [
    {
        'product_id': 'MOB-001',
        'name': 'Samsung Galaxy M14 5G (6GB/128GB)',
        'category': 'Smartphones',
        'cost_price': 12500.00,  # INR
        'gst_percent': 18,
        'base_price': 15999.00,
        'competitor_base': 15499.00
    },
    {
        'product_id': 'MOB-002',
        'name': 'Redmi Note 13 Pro (8GB/256GB)',
        'category': 'Smartphones',
        'cost_price': 18000.00,
        'gst_percent': 18,
        'base_price': 23999.00,
        'competitor_base': 23499.00
    },
    {
        'product_id': 'ACC-001',
        'name': 'Tempered Glass Screen Protector',
        'category': 'Accessories',
        'cost_price': 45.00,
        'gst_percent': 18,
        'base_price': 149.00,
        'competitor_base': 99.00
    },
    {
        'product_id': 'ACC-002',
        'name': 'Fast Charger 33W Type-C',
        'category': 'Accessories',
        'cost_price': 280.00,
        'gst_percent': 18,
        'base_price': 599.00,
        'competitor_base': 549.00
    },
    {
        'product_id': 'ACC-003',
        'name': 'Wireless Earbuds TWS Bluetooth',
        'category': 'Accessories',
        'cost_price': 450.00,
        'gst_percent': 18,
        'base_price': 999.00,
        'competitor_base': 899.00
    },
    {
        'product_id': 'MOB-003',
        'name': 'Realme Narzo 60 5G (8GB/128GB)',
        'category': 'Smartphones',
        'cost_price': 14200.00,
        'gst_percent': 18,
        'base_price': 18999.00,
        'competitor_base': 18499.00
    },
    {
        'product_id': 'ACC-004',
        'name': 'Silicone Back Cover Case',
        'category': 'Accessories',
        'cost_price': 65.00,
        'gst_percent': 18,
        'base_price': 199.00,
        'competitor_base': 149.00
    },
    {
        'product_id': 'ACC-005',
        'name': 'Power Bank 10000mAh Fast Charging',
        'category': 'Accessories',
        'cost_price': 580.00,
        'gst_percent': 18,
        'base_price': 1199.00,
        'competitor_base': 1099.00
    }
]


def normalize_product_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize product payload from either:
    - Canonical backend schema (product_id, cost_price, current_price, ...)
    - Frontend view schema (id, cost, currentPrice, demandScore, ...)
    """
    product_id = raw.get('product_id') or raw.get('id')
    if not product_id:
        raise ValueError("Product is missing product_id/id")

    name = raw.get('name', product_id)
    category = raw.get('category', 'General')
    seller_id = raw.get('seller_id', 'SELLER-001')  # Default seller

    cost_price = float(raw.get('cost_price', raw.get('cost', 0)) or 0)
    current_price = float(raw.get('current_price', raw.get('currentPrice', raw.get('base_price', 0))) or 0)
    competitor_base = float(
        raw.get('competitor_base', raw.get('competitor_price', raw.get('competitorPrice', 0))) or 0
    )
    gst_percent = float(raw.get('gst_percent', raw.get('gstRate', 18)) or 18)
    demand_factor = float(raw.get('demand_factor', raw.get('demandScore', 1.0)) or 1.0)

    if current_price <= 0 and cost_price > 0:
        current_price = round(cost_price * 1.3, 2)
    if competitor_base <= 0:
        competitor_base = round(current_price * 0.95, 2) if current_price > 0 else round(cost_price * 1.25, 2)

    return {
        'product_id': str(product_id),
        'seller_id': str(seller_id),
        'name': str(name),
        'category': str(category),
        'cost_price': round(cost_price, 2),
        'gst_percent': round(gst_percent, 2),
        'base_price': round(current_price, 2),
        'competitor_base': round(competitor_base, 2),
        'sku': raw.get('sku', product_id),
        'inventory_level': int(raw.get('inventory_level', raw.get('inventoryLevel', 100)) or 100),
        'status': raw.get('status', 'stable'),
        'demand_factor': round(demand_factor, 2),
        'updated_at': raw.get('updated_at', raw.get('lastUpdated', generate_timestamp()))
    }


def load_products_from_file() -> List[Dict[str, Any]]:
    """
    Load optional seed data from repository-level data/product.json.
    """
    data_file = Path(__file__).resolve().parents[2] / 'data' / 'product.json'
    if not data_file.exists():
        return []

    try:
        payload = json.loads(data_file.read_text(encoding='utf-8'))
        if not isinstance(payload, list):
            logger.warning("data/product.json found but not a list; ignoring")
            return []
        normalized = [normalize_product_record(item) for item in payload]
        logger.info(f"Loaded {len(normalized)} products from {data_file}")
        return normalized
    except Exception as e:
        logger.warning(f"Failed to load data/product.json: {e}")
        return []


def resolve_seed_products(request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Resolve seed products from request, file, or built-in defaults.
    Priority:
    1) request.products
    2) data/product.json
    3) SAMPLE_PRODUCTS
    """
    if isinstance(request.get('products'), list) and request['products']:
        return [normalize_product_record(item) for item in request['products']]

    from_file = load_products_from_file()
    if from_file:
        return from_file

    return [normalize_product_record(item) for item in SAMPLE_PRODUCTS]


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
        'Smartphones': 1.2,
        'Accessories': 1.0
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


import json
from decimal import Decimal

def _to_decimal(obj):
    return json.loads(json.dumps(obj), parse_float=Decimal)

def initialize_sample_products(seed_products: List[Dict[str, Any]]) -> List[Dict]:
    """
    Initialize sample products in DynamoDB if they don't exist.
    """
    table = dynamodb.Table(PRODUCTS_TABLE)
    initialized = []

    for product in seed_products:
        try:
            # Check if product exists
            existing = table.get_item(Key={'product_id': product['product_id']})

            if 'Item' not in existing:
                # Create new product
                item = _to_decimal({
                    'product_id': product['product_id'],
                    'seller_id': product.get('seller_id', 'SELLER-001'),
                    'name': product['name'],
                    'category': product['category'],
                    'sku': product.get('sku', product['product_id']),
                    'cost_price': product['cost_price'],
                    'gst_percent': product['gst_percent'],
                    'current_price': product['base_price'],
                    'competitor_price': product['competitor_base'],
                    'demand_factor': product.get('demand_factor', 1.0),
                    'inventory_level': product.get('inventory_level', 100),
                    'status': product.get('status', 'stable'),
                    'market_trend': 'stable',
                    'margin_percent': round(
                        ((product['base_price'] - product['cost_price'] * (1 + product['gst_percent']/100))
                         / product['base_price']) * 100, 2
                    ),
                    'created_at': generate_timestamp(),
                    'updated_at': product.get('updated_at', generate_timestamp())
                })
                table.put_item(Item=item)
                initialized.append(product['product_id'])
                logger.info(f"Initialized product: {product['product_id']}")

        except Exception as e:
            logger.error(f"Error initializing product {product['product_id']}: {e}")

    return initialized


def simulate_market_event(seed_products: List[Dict[str, Any]], product_id: str = None, event_type: str = 'normal') -> Dict[str, Any]:
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
        product = next((p for p in seed_products if p['product_id'] == product_id), None)
        if not product:
            product = random.choice(seed_products)
    else:
        product = random.choice(seed_products)

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
        # Extract request payload (supports API Gateway and direct invokes)
        request = event
        if 'body' in event and event['body']:
            request = json.loads(event['body']) if isinstance(event['body'], str) else event['body']

        # Resolve and initialize seed products if needed
        seed_products = resolve_seed_products(request if isinstance(request, dict) else {})
        initialized = initialize_sample_products(seed_products)
        if initialized:
            logger.info(f"Initialized {len(initialized)} sample products")

        # Determine simulation mode
        mode = request.get('mode', 'single') if isinstance(request, dict) else 'single'
        event_type = request.get('event_type', 'normal') if isinstance(request, dict) else 'normal'
        product_id = request.get('product_id') if isinstance(request, dict) else None

        results = []

        if mode == 'batch':
            # Simulate for all products
            for product in seed_products:
                sim_event = simulate_market_event(seed_products, product['product_id'], event_type)
                sent = send_to_eventbridge(sim_event)
                results.append({
                    'product_id': product['product_id'],
                    'sent': sent,
                    'competitor_price': sim_event['competitor_price'],
                    'demand_factor': sim_event['demand_factor']
                })

        elif mode == 'scenario':
            # Run a predefined scenario (for demos)
            scenarios = request.get('scenarios', [
                {'event_type': 'price_drop', 'delay': 0},
                {'event_type': 'demand_surge', 'delay': 5}
            ])

            for scenario in scenarios:
                sim_event = simulate_market_event(
                    seed_products,
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
            sim_event = simulate_market_event(seed_products, product_id, event_type)
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
