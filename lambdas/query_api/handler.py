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
        
        # Calculate AI confidence from recent decisions with corrections
        decisions = db.scan(DECISIONS_TABLE)
        corrections = db.scan(CORRECTIONS_TABLE)
        
        if decisions:
            # Count decisions that were NOT corrected (i.e., AI was right)
            corrected_decision_ids = {c.get('decision_id') for c in corrections}
            correct_decisions = [d for d in decisions if d.get('decision_id') not in corrected_decision_ids]
            
            # AI confidence = % of decisions that didn't need correction
            ai_confidence = (len(correct_decisions) / len(decisions)) * 100
        else:
            ai_confidence = None  # No data yet - don't show misleading number
        
        result = {
            'activeProducts': active_products,
            'avgMargin': round(avg_margin, 1),
            'revenueToday': round(revenue_today, 2),
            'aiConfidence': round(ai_confidence, 1) if ai_confidence is not None else None,
            'activeProductsDelta': None,  # Requires historical data
            'avgMarginDelta': None,  # Requires historical data
            'revenueDelta': None,  # Requires historical data
            'confidenceDelta': None  # Requires historical data
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
    """GET /analytics/revenue - Calculate actual revenue from pricing decisions"""
    try:
        decisions = db.scan(DECISIONS_TABLE)
        products = db.scan(PRODUCTS_TABLE)
        
        # Group decisions by date
        revenue_by_date = {}
        
        for decision in decisions:
            timestamp = decision.get('timestamp', '')
            if not timestamp:
                continue
            
            date = timestamp.split('T')[0]  # Extract date from ISO timestamp
            
            if date not in revenue_by_date:
                revenue_by_date[date] = {'our_revenue': 0, 'competitor_revenue': 0}
            
            # Get product details
            product_id = decision.get('product_id')
            product = next((p for p in products if p.get('product_id') == product_id), None)
            
            if product:
                # Calculate revenue from this decision
                new_price = float(decision.get('output_data', {}).get('recommended_price', 0))
                competitor_price = float(product.get('competitor_price', 0))
                demand_factor = float(product.get('demand_factor', 1.0))
                
                # Estimate daily sales (simplified: demand_factor * 10 units)
                estimated_units = demand_factor * 10
                
                revenue_by_date[date]['our_revenue'] += new_price * estimated_units
                revenue_by_date[date]['competitor_revenue'] += competitor_price * estimated_units
        
        # If no decisions yet, return empty array
        if not revenue_by_date:
            return {'statusCode': 200, 'body': json.dumps([])}
        
        # Convert to array and sort by date
        result = [
            {
                'date': date,
                'revenue': round(data['our_revenue'], 2),
                'competitor': round(data['competitor_revenue'], 2)
            }
            for date, data in sorted(revenue_by_date.items())
        ]
        
        # Return last 7 days only
        return {'statusCode': 200, 'body': json.dumps(result[-7:])}
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
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


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
