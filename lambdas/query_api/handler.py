"""
Query API Lambda - Handles all GET requests for frontend
"""

import json
import os
import sys
from typing import Any, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import boto3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    DynamoDBClient,
    setup_logger,
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    CORRECTIONS_TABLE
)

logger = setup_logger(__name__)
db = DynamoDBClient()
sf_client = boto3.client('stepfunctions')


def get_products():
    """GET /products"""
    try:
        products = db.scan(PRODUCTS_TABLE)
        result = []
        for p in products:
            cost = float(p.get('cost_price', 0))
            current = float(p.get('current_price', 0))
            competitor = float(p.get('competitor_price', current))
            margin = ((current - cost * 1.18) / current * 100) if current > 0 else 0
            
            result.append({
                'id': p.get('product_id'),
                'name': p.get('name', p.get('product_id')),
                'cost': cost,
                'currentPrice': current,
                'competitorPrice': competitor,
                'margin': round(margin, 2),
                'status': p.get('status', 'stable'),
                'category': p.get('category', 'General'),
                'lastUpdated': p.get('updated_at', datetime.now().isoformat()),
                'sku': p.get('sku', p.get('product_id')),
                'inventoryLevel': int(p.get('inventory_level', 100)),
                'demandScore': float(p.get('demand_factor', 1.0))
            })
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    except Exception as e:
        logger.exception(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_dashboard_kpis():
    """GET /dashboard/kpis"""
    try:
        products = db.scan(PRODUCTS_TABLE)
        active_products = len(products)
        
        total_margin = 0
        revenue_today = 0
        for p in products:
            cost = float(p.get('cost_price', 0))
            current = float(p.get('current_price', 0))
            margin = ((current - cost * 1.18) / current * 100) if current > 0 else 0
            total_margin += margin
            revenue_today += current * float(p.get('demand_factor', 1.0)) * 10
        
        avg_margin = total_margin / max(active_products, 1)
        
        result = {
            'activeProducts': active_products,
            'avgMargin': round(avg_margin, 1),
            'revenueToday': round(revenue_today, 2),
            'aiConfidence': 85.0,
            'activeProductsDelta': 2,
            'avgMarginDelta': 1.2,
            'revenueDelta': 8.5,
            'confidenceDelta': 2.1
        }
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    except Exception as e:
        logger.exception(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_recent_decisions():
    """GET /decisions/recent"""
    try:
        decisions = db.scan(DECISIONS_TABLE)
        sorted_decisions = sorted(decisions, key=lambda x: x.get('timestamp', ''), reverse=True)[:20]
        
        result = []
        for d in sorted_decisions:
            product_id = d.get('product_id', 'UNKNOWN')
            product = db.get_item(PRODUCTS_TABLE, {'product_id': product_id})
            product_name = product.get('name', product_id) if product else product_id
            
            old_price = float(d.get('input_data', {}).get('current_price', 0))
            new_price = float(d.get('output_data', {}).get('recommended_price', 0))
            
            result.append({
                'id': d.get('decision_id'),
                'productId': product_id,
                'productName': product_name,
                'oldPrice': old_price,
                'newPrice': new_price,
                'reason': d.get('pricing_strategy', 'Price optimization'),
                'confidence': float(d.get('output_data', {}).get('confidence', 0.85)),
                'type': 'deterministic',
                'timestamp': d.get('timestamp', datetime.now().isoformat()),
                'status': 'success',
                'description': d.get('pricing_strategy', 'Price optimization'),
                'payload': {'oldPrice': old_price, 'newPrice': new_price}
            })
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    except Exception as e:
        logger.exception(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_alerts():
    """GET /alerts"""
    try:
        products = db.scan(PRODUCTS_TABLE)
        alerts = []
        
        for p in products:
            cost = float(p.get('cost_price', 0))
            current = float(p.get('current_price', 0))
            margin = ((current - cost * 1.18) / current * 100) if current > 0 else 0
            
            if margin < 10:
                alerts.append({
                    'id': f"ALERT-{p.get('product_id')}",
                    'type': 'warning',
                    'message': f'Margin below 10% ({margin:.1f}%)',
                    'productName': p.get('name', p.get('product_id')),
                    'timestamp': datetime.now().isoformat(),
                    'acknowledged': False
                })
        
        return {'statusCode': 200, 'body': json.dumps(alerts[:10])}
    except Exception as e:
        logger.exception(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_revenue_analytics():
    """GET /analytics/revenue"""
    try:
        result = []
        base_revenue = 42000
        base_competitor = 38000
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            result.append({
                'date': date,
                'revenue': base_revenue + i * 500,
                'competitor': base_competitor + i * 400
            })
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    except Exception as e:
        logger.exception(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_simulation_status(execution_arn: str):
    """GET /simulate/:runId/status"""
    try:
        response = sf_client.describe_execution(executionArn=execution_arn)
        status = response['status']  # RUNNING, SUCCEEDED, FAILED, TIMED_OUT, ABORTED
        
        result = {
            'runId': execution_arn.split(':')[-1],
            'status': status,
            'steps': [
                {'id': 'simulate_event', 'name': 'Generate Market Event', 'status': 'completed', 'duration': 450},
                {'id': 'market_processor', 'name': 'Process Market Data', 'status': 'completed', 'duration': 680},
                {'id': 'pricing_engine', 'name': 'Calculate Price', 'status': 'completed' if status == 'SUCCEEDED' else 'running', 'duration': 520},
                {'id': 'guardrail_executor', 'name': 'Validate Guardrails', 'status': 'completed' if status == 'SUCCEEDED' else 'pending', 'duration': 380},
                {'id': 'monitoring_agent', 'name': 'Monitor Deviations', 'status': 'completed' if status == 'SUCCEEDED' else 'pending', 'duration': 420},
            ],
            'result': {
                'decisionsApplied': 1,
                'decisionsBlocked': 0,
                'avgConfidence': 0.89
            }
        }
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    except Exception as e:
        logger.exception(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    logger.info(f"Query API invoked: {json.dumps(event, default=str)[:500]}")
    
    try:
        path = event.get('rawPath', event.get('path', ''))
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
        if method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        # Route to handlers
        if path == '/products':
            response = get_products()
        elif path == '/dashboard/kpis':
            response = get_dashboard_kpis()
        elif path == '/decisions/recent' or path == '/decisions/log':
            response = get_recent_decisions()
        elif path == '/alerts':
            response = get_alerts()
        elif path == '/analytics/revenue':
            response = get_revenue_analytics()
        elif path.startswith('/simulate/') and path.endswith('/status'):
            # Extract execution ARN from path: /simulate/{runId}/status
            run_id = path.split('/')[2]
            # Reconstruct execution ARN
            state_machine_arn = os.environ.get('STATE_MACHINE_ARN', '')
            execution_arn = f"{state_machine_arn.rsplit(':', 1)[0]}:execution:{state_machine_arn.split(':')[-1]}:{run_id}"
            response = get_simulation_status(execution_arn)
        else:
            response = {'statusCode': 404, 'body': json.dumps({'error': f'Not found: {path}'})}
        
        response['headers'] = headers
        return response
        
    except Exception as e:
        logger.exception(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
