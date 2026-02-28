"""
Bedrock Test Lambda Handler

Tests the Bedrock inference profile integration with Claude Haiku 4.5.
Deploy this single Lambda first to validate Bedrock access before wiring the full system.

Usage:
1. Create inference profile in Bedrock console (us-east-1)
2. Copy the ARN
3. Deploy this Lambda with INFERENCE_PROFILE_ARN env variable
4. Test with the sample event
"""

import json
import boto3
import os
from typing import Dict, Any
from botocore.exceptions import ClientError

# Environment variables
INFERENCE_PROFILE_ARN = os.environ.get('INFERENCE_PROFILE_ARN', '')
BEDROCK_REGION = os.environ.get('BEDROCK_REGION', 'us-east-1')

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name=BEDROCK_REGION
)


def invoke_bedrock(prompt: str, max_tokens: int = 300, temperature: float = 0.3) -> Dict[str, Any]:
    """
    Invoke Claude Haiku 4.5 via Bedrock inference profile.

    Args:
        prompt: The user prompt to send to Claude
        max_tokens: Maximum tokens in response
        temperature: Response randomness (0-1)

    Returns:
        Structured response with reasoning
    """
    if not INFERENCE_PROFILE_ARN:
        return {
            'success': False,
            'error': 'INFERENCE_PROFILE_ARN environment variable not set',
            'reasoning': None,
            'model_used': None
        }

    # Claude 4.5 Haiku request format
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = bedrock_runtime.invoke_model(
            modelId=INFERENCE_PROFILE_ARN,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())

        # Parse Claude response
        content = response_body.get('content', [])
        reasoning = content[0].get('text', '') if content else ''

        return {
            'success': True,
            'reasoning': reasoning,
            'model_used': 'Claude Haiku 4.5',
            'model_id': INFERENCE_PROFILE_ARN,
            'usage': response_body.get('usage', {}),
            'stop_reason': response_body.get('stop_reason', '')
        }

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))

        # Handle specific error types
        if error_code == 'AccessDeniedException':
            return {
                'success': False,
                'error': 'AccessDeniedException: Check inference profile ARN and permissions',
                'error_code': error_code,
                'reasoning': None,
                'model_used': None
            }
        elif error_code == 'ValidationException':
            return {
                'success': False,
                'error': f'ValidationException: {error_message}',
                'error_code': error_code,
                'reasoning': None,
                'model_used': None
            }
        elif error_code == 'ThrottlingException':
            return {
                'success': False,
                'error': 'ThrottlingException: Request rate exceeded, please retry',
                'error_code': error_code,
                'reasoning': None,
                'model_used': None
            }
        else:
            return {
                'success': False,
                'error': f'{error_code}: {error_message}',
                'error_code': error_code,
                'reasoning': None,
                'model_used': None
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'error_type': type(e).__name__,
            'reasoning': None,
            'model_used': None
        }


def test_pricing_reasoning(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test Bedrock with a pricing reasoning prompt.

    This simulates the actual use case in the correction agent.
    """
    prompt = f"""You are an AI pricing analyst for an e-commerce platform.

Product: {product_data.get('name', 'Unknown')}
Category: {product_data.get('category', 'Unknown')}
Current Price: ₹{product_data.get('current_price', 0)}
Cost Price: ₹{product_data.get('cost_price', 0)}
Competitor Price: ₹{product_data.get('competitor_price', 0)}
Predicted Sales: {product_data.get('predicted_sales', 0)} units
Actual Sales: {product_data.get('actual_sales', 0)} units

The actual sales deviated from prediction by {product_data.get('deviation_percent', 0):.1f}%.

Analyze this situation briefly and suggest:
1. Root cause of the deviation (one sentence)
2. Recommended price adjustment (if any)
3. Confidence level (low/medium/high)

Keep your response under 100 words."""

    return invoke_bedrock(prompt, max_tokens=300, temperature=0.3)


def test_simple_query(query: str) -> Dict[str, Any]:
    """
    Test Bedrock with a simple query.
    """
    return invoke_bedrock(query, max_tokens=200, temperature=0.3)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point for Bedrock testing.

    Test event formats:

    1. Simple test:
    {
        "test_type": "simple",
        "query": "What is 2+2?"
    }

    2. Pricing reasoning test:
    {
        "test_type": "pricing",
        "product_data": {
            "name": "Wireless Earbuds",
            "category": "Electronics",
            "current_price": 899,
            "cost_price": 450,
            "competitor_price": 799,
            "predicted_sales": 100,
            "actual_sales": 70,
            "deviation_percent": 30
        }
    }

    3. Configuration check:
    {
        "test_type": "config"
    }
    """
    print(f"Bedrock Test Lambda invoked: {json.dumps(event, default=str)}")

    test_type = event.get('test_type', 'simple')

    # Configuration check
    if test_type == 'config':
        return {
            'statusCode': 200,
            'body': json.dumps({
                'inference_profile_arn': INFERENCE_PROFILE_ARN,
                'bedrock_region': BEDROCK_REGION,
                'arn_configured': bool(INFERENCE_PROFILE_ARN),
                'status': 'ready' if INFERENCE_PROFILE_ARN else 'missing_arn'
            })
        }

    # Simple query test
    if test_type == 'simple':
        query = event.get('query', 'Hello, can you confirm you are Claude Haiku 4.5?')
        result = test_simple_query(query)
        return {
            'statusCode': 200 if result['success'] else 500,
            'body': json.dumps(result, default=str)
        }

    # Pricing reasoning test
    if test_type == 'pricing':
        product_data = event.get('product_data', {
            'name': 'Test Product',
            'category': 'Electronics',
            'current_price': 999,
            'cost_price': 500,
            'competitor_price': 899,
            'predicted_sales': 100,
            'actual_sales': 70,
            'deviation_percent': 30
        })
        result = test_pricing_reasoning(product_data)
        return {
            'statusCode': 200 if result['success'] else 500,
            'body': json.dumps(result, default=str)
        }

    # Default: unknown test type
    return {
        'statusCode': 400,
        'body': json.dumps({
            'error': f'Unknown test_type: {test_type}',
            'supported_types': ['simple', 'pricing', 'config']
        })
    }


# Sample test events for reference
SAMPLE_EVENTS = {
    'config_check': {
        'test_type': 'config'
    },
    'simple_test': {
        'test_type': 'simple',
        'query': 'What is 2+2? Just give me the number.'
    },
    'pricing_test': {
        'test_type': 'pricing',
        'product_data': {
            'name': 'Wireless Bluetooth Earbuds',
            'category': 'Electronics',
            'current_price': 899,
            'cost_price': 450,
            'competitor_price': 799,
            'predicted_sales': 100,
            'actual_sales': 70,
            'deviation_percent': 30
        }
    }
}