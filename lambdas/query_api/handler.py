"""
Query API Lambda - Handles all GET requests for frontend

Minimal MVP implementation for hackathon demo.
Single Lambda handles: products, dashboard, decisions, alerts, analytics.
"""

import json
import os
import sys
from typing import Any, Dict, List
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    DynamoDBClient,
    setup_logger,
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    CORRECTIONS_TABLE,
    STATUS_SUCCESS,
    STATUS_FAILED
)

logger = setup_logger(__name__)
db = DynamoDBClient()


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def get_products() -> Dict[str, Any]:
    """GET /products - List all products."""
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
                'lastUpdated': p.get('updated_at', p.get('created_at', datetime.now().isoformat())),
                'sku': p.get('sku', p.get('product_id')),
                'inventoryLevel': int(p.get('inventory_level', 100)),
                'demandScore': float(p.get('demand_factor', 1.0))
            })
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    
    except Exception as e:
        logger.exception(f"Error fetching products: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_product_detail(product_id: str) -> Dict[str, Any]:
    """GET /products/:id - Product details with history."""
    try:
        product = db.get_item(PRODUCTS_TABLE, {'product_id': product_id})
        if not product:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Product not found'})}
        
        # Get decisions for this product
        decisions = db.scan(
            DECISIONS_TABLE,
            filter_expression='product_id = :pid',
            expression_values={':pid': product_id}
        )
        
        cost = float(product.get('cost_price', 0))
        current = float(product.get('current_price', 0))
        competitor = float(product.get('competitor_price', current))
        margin = ((current - cost * 1.18) / current * 100) if current > 0 else 0
        
        # Format decisions
        formatted_decisions = []
        for d in decisions[:10]:
            old_price = float(d.get('input_data', {}).get('current_price', 0))
            new_price = float(d.get('output_data', {}).get('recommended_price', 0))
            formatted_decisions.append({
                'id': d.get('decision_id'),
                'productId': product_id,
                'productName': product.get('name', product_id),
                'oldPrice': old_price,
                'newPrice': new_price,
                'reason': d.get('pricing_strategy', 'Price optimization'),
                'confidence': float(d.get('output_data', {}).get('confidence', 0.85)),
                'type': d.get('decision_type', 'deterministic'),
                'timestamp': d.get('timestamp', datetime.now().isoformat()),
                'status': d.get('status', 'applied')
            })
        
        # Generate mock historical prices (last 7 days)
        historical = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            historical.append({
                'date': date,
                'price': current + (i - 3) * 10,
                'competitorPrice': competitor + (i - 3) * 8
            })
        
        result = {
            'id': product_id,
            'name': product.get('name', product_id),
            'cost': cost,
            'currentPrice': current,
            'competitorPrice': competitor,
            'margin': round(margin, 2),
            'status': product.get('status', 'stable'),
            'category': product.get('category', 'General'),
            'lastUpdated': product.get('updated_at', datetime.now().isoformat()),
            'historicalPrices': historical,
            'decisions': formatted_decisions
        }
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    
    except Exception as e:
        logger.exception(f"Error fetching product detail: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_dashboard_kpis() -> Dict[str, Any]:
    """GET /dashboard/kpis - Dashboard metrics."""
    try:
        products = db.scan(PRODUCTS_TABLE)
        decisions = db.scan(DECISIONS_TABLE)
        
        active_products = len(products)
        
        # Calculate average margin
        total_margin = 0
        revenue_today = 0
        for p in products:
            cost = float(p.get('cost_price', 0))
            current = float(p.get('current_price', 0))
            margin = ((current - cost * 1.18) / current * 100) if current > 0 else 0
            total_margin += margin
            revenue_today += current * float(p.get('demand_factor', 1.0)) * 10
        
        avg_margin = total_margin / max(active_products, 1)
        
        # AI confidence from recent decisions
        recent_decisions = [d for d in decisions if d.get('status') in ['approved', 'completed']][:20]
        ai_confidence = sum(float(d.get('output_data', {}).get('confidence', 0.85)) for d in recent_decisions) / max(len(recent_decisions), 1) * 100
        
        result = {
            'activeProducts': active_products,
            'avgMargin': round(avg_margin, 1),
            'revenueToday': round(revenue_today, 2),
            'aiConfidence': round(ai_confidence, 1),
            'activeProductsDelta': 2,
            'avgMarginDelta': 1.2,
            'revenueDelta': 8.5,
            'confidenceDelta': 2.1
        }
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    
    except Exception as e:
        logger.exception(f"Error calculating KPIs: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_recent_decisions() -> Dict[str, Any]:
    """GET /decisions/recent - Recent pricing decisions."""
    try:
        decisions = db.scan(DECISIONS_TABLE)
        
        # Sort by timestamp and get recent 20
        sorted_decisions = sorted(
            decisions,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )[:20]
        
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
                'type': d.get('decision_type', 'deterministic'),
                'timestamp': d.get('timestamp', datetime.now().isoformat()),
                'status': d.get('status', 'applied')
            })
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    
    except Exception as e:
        logger.exception(f"Error fetching decisions: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_alerts() -> Dict[str, Any]:
    """GET /alerts - Active alerts."""
    try:
        products = db.scan(PRODUCTS_TABLE)
        corrections = db.scan(CORRECTIONS_TABLE)
        
        alerts = []
        
        # Check for low margin products
        for p in products:
            cost = float(p.get('cost_price', 0))
            current = float(p.get('current_price', 0))
            margin = ((current - cost * 1.18) / current * 100) if current > 0 else 0
            
            if margin < 10:
                alerts.append({
                    'id': f"ALERT-{p.get('product_id')}",
                    'type': 'warning',
                    'message': f'Margin below 10% threshold ({margin:.1f}%)',
                    'productName': p.get('name', p.get('product_id')),
                    'timestamp': datetime.now().isoformat(),
                    'acknowledged': False
                })
        
        # Add correction alerts
        for c in corrections[:5]:
            if c.get('status') == 'pending':
                alerts.append({
                    'id': c.get('correction_id'),
                    'type': 'info',
                    'message': 'AI correction pending approval',
                    'productName': c.get('product_id', 'Unknown'),
                    'timestamp': c.get('timestamp', datetime.now().isoformat()),
                    'acknowledged': False
                })
        
        return {'statusCode': 200, 'body': json.dumps(alerts[:10])}
    
    except Exception as e:
        logger.exception(f"Error fetching alerts: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_revenue_analytics() -> Dict[str, Any]:
    """GET /analytics/revenue - Revenue trends."""
    try:
        # Generate mock revenue data for last 7 days
        result = []
        base_revenue = 42000
        base_competitor = 38000
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            result.append({
                'date': date,
                'revenue': base_revenue + i * 500 + (i % 2) * 300,
                'competitor': base_competitor + i * 400 + (i % 2) * 200
            })
        
        return {'statusCode': 200, 'body': json.dumps(result)}
    
    except Exception as e:
        logger.exception(f"Error fetching analytics: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler - routes based on path.
    
    Handles:
    - GET /products
    - GET /products/{id}
    - GET /dashboard/kpis
    - GET /decisions/recent
    - GET /alerts
    - GET /analytics/revenue
    """
    logger.info(f"Query API invoked: {json.dumps(event, default=str)[:500]}")
    
    try:
        path = event.get('rawPath', event.get('path', ''))
        method = event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod', 'GET'))
        
        # CORS headers
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
        # Handle OPTIONS for CORS
        if method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        # Route to appropriate handler
        if path == '/products':
            response = get_products()
        elif path.startswith('/products/') and '/history' not in path:
            product_id = path.split('/')[-1]
            response = get_product_detail(product_id)
        elif path == '/dashboard/kpis':
            response = get_dashboard_kpis()
        elif path == '/decisions/recent':
            response = get_recent_decisions()
        elif path == '/alerts':
            response = get_alerts()
        elif path == '/analytics/revenue':
            response = get_revenue_analytics()
        else:
            response = {
                'statusCode': 404,
                'body': json.dumps({'error': f'Path not found: {path}'})
            }
        
        # Add CORS headers to response
        response['headers'] = headers
        return response
    
    except Exception as e:
        logger.exception(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
