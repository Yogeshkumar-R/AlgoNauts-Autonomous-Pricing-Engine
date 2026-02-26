"""
Correction Agent Lambda Handler

Handles price corrections using AWS Bedrock (Claude) for AI-powered reasoning.
Generates explanations and revised pricing recommendations.
"""

import json
from typing import Any, Dict, Optional
import sys
import os

import boto3
from botocore.exceptions import ClientError

# Add shared module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    DynamoDBClient,
    setup_logger,
    validate_required_fields,
    generate_timestamp,
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    CORRECTIONS_TABLE,
    BEDROCK_MODEL_ID,
    BEDROCK_REGION,
    STATUS_SUCCESS,
    STATUS_FAILED
)

logger = setup_logger(__name__)
db_client = DynamoDBClient()

# Initialize Bedrock client (lazy)
_bedrock_client = None


def get_bedrock_client():
    """Get or create Bedrock runtime client."""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=BEDROCK_REGION
        )
    return _bedrock_client


def build_analysis_prompt(
    product_data: Dict[str, Any],
    decision_data: Dict[str, Any],
    performance_data: Dict[str, Any],
    deviation_data: Dict[str, Any]
) -> str:
    """
    Build the prompt for Bedrock Claude model analysis.

    Args:
        product_data: Product information
        decision_data: Original pricing decision
        performance_data: Actual performance metrics
        deviation_data: Deviation analysis

    Returns:
        Formatted prompt string
    """
    prompt = f"""You are an AI pricing analyst for an autonomous pricing system. Analyze the following pricing deviation and provide a revised recommendation.

PRODUCT INFORMATION:
- Product ID: {product_data.get('product_id', 'unknown')}
- Cost Price: ₹{decision_data['input_data'].get('cost_price', 0):.2f}
- GST Percent: {decision_data['input_data'].get('gst_percent', 0)}%
- Current Price: ₹{performance_data.get('current_price', 0):.2f}
- Competitor Price: ₹{decision_data['input_data'].get('competitor_price', 0):.2f}
- Demand Factor: {decision_data['input_data'].get('demand_factor', 1.0)}

ORIGINAL PRICING DECISION:
- Recommended Price: ₹{decision_data['output_data'].get('recommended_price', 0):.2f}
- Predicted Sales: {decision_data['output_data'].get('predicted_sales', 0)} units
- Predicted Margin: {decision_data['output_data'].get('predicted_margin', 0):.2f}%
- Pricing Strategy: {decision_data.get('pricing_strategy', 'unknown')}

ACTUAL PERFORMANCE:
- Actual Sales: {performance_data.get('actual_sales', 0)} units
- Actual Margin: {performance_data.get('actual_margin', 0):.2f}%

DEVIATION ANALYSIS:
- Sales Deviation: {deviation_data.get('percent', 0):.2f}% ({deviation_data.get('direction', 'unknown')})
- Threshold Exceeded: Yes (threshold: 20%)

TASK:
1. Analyze why the prediction deviated significantly from actual performance
2. Identify potential factors that were not considered
3. Recommend a revised price with justification
4. Provide confidence level (high/medium/low)

Respond in JSON format with the following structure:
{{
    "analysis": "Brief analysis of what went wrong",
    "factors": ["factor1", "factor2", ...],
    "revised_price": <float>,
    "revised_predicted_sales": <int>,
    "revised_predicted_margin": <float>,
    "confidence": "high|medium|low",
    "explanation": "Detailed explanation for stakeholders",
    "recommendations": ["recommendation1", "recommendation2", ...]
}}
"""
    return prompt


def call_bedrock_claude(prompt: str) -> Dict[str, Any]:
    """
    Call AWS Bedrock Claude model for analysis.

    Args:
        prompt: Analysis prompt

    Returns:
        Parsed JSON response from Claude

    Raises:
        Exception: If Bedrock call fails
    """
    try:
        client = get_bedrock_client()

        # Prepare request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "temperature": 0.3,  # Lower temperature for more deterministic pricing
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        logger.info(f"Calling Bedrock model: {BEDROCK_MODEL_ID}")

        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())

        # Extract content from Claude response
        content = response_body.get('content', [])
        if content and len(content) > 0:
            text_response = content[0].get('text', '{}')
        else:
            text_response = '{}'

        # Parse JSON response
        # Handle potential markdown code blocks
        text_response = text_response.strip()
        if text_response.startswith('```json'):
            text_response = text_response[7:]
        if text_response.startswith('```'):
            text_response = text_response[3:]
        if text_response.endswith('```'):
            text_response = text_response[:-3]

        parsed_response = json.loads(text_response.strip())

        logger.info("Successfully received Bedrock response")
        return parsed_response

    except ClientError as e:
        logger.error(f"Bedrock API error: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Bedrock response: {e}")
        # Return fallback response
        return {
            "analysis": "Failed to parse AI response",
            "factors": ["api_error"],
            "revised_price": None,
            "confidence": "low",
            "explanation": f"AI response parsing failed: {str(e)}",
            "recommendations": ["Manual review required"]
        }
    except Exception as e:
        logger.exception(f"Unexpected error calling Bedrock: {e}")
        raise


def generate_fallback_correction(
    decision_data: Dict[str, Any],
    performance_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate fallback correction when Bedrock is unavailable.

    Args:
        decision_data: Original decision data
        performance_data: Performance metrics

    Returns:
        Fallback correction recommendation
    """
    # Simple adjustment based on deviation
    actual_sales = performance_data.get('actual_sales', 0)
    predicted_sales = performance_data.get('predicted_sales', 1)

    current_price = performance_data.get('current_price', 0)
    cost_price = decision_data['input_data'].get('cost_price', 0)
    gst_percent = decision_data['input_data'].get('gst_percent', 18)

    sales_ratio = actual_sales / predicted_sales if predicted_sales > 0 else 1.0

    # Adjust price inversely to sales ratio
    if sales_ratio < 0.8:  # Underperforming
        price_adjustment = 1 - ((1 - sales_ratio) * 0.5)  # Reduce price
    elif sales_ratio > 1.2:  # Overperforming
        price_adjustment = 1 + ((sales_ratio - 1) * 0.3)  # Increase price
    else:
        price_adjustment = 1.0  # No change

    revised_price = current_price * price_adjustment

    # Ensure minimum margin
    min_price = cost_price * (1 + gst_percent / 100) * 1.05
    revised_price = max(revised_price, min_price)

    return {
        "analysis": "Fallback correction (AI unavailable)",
        "factors": ["bedrock_unavailable", "algorithmic_adjustment"],
        "revised_price": round(revised_price, 2),
        "revised_predicted_sales": int(actual_sales * 1.1),
        "revised_predicted_margin": round(((revised_price - cost_price * (1 + gst_percent/100)) / revised_price) * 100, 2),
        "confidence": "low",
        "explanation": "Correction generated using fallback algorithm due to AI service unavailability.",
        "recommendations": [
            "Review manually when possible",
            "Monitor sales closely for next period",
            "Consider competitor price changes"
        ]
    }


def run_correction(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute correction logic using Bedrock AI analysis.

    Args:
        event: Correction event containing:
            - correction_id: ID of the correction event
            - product_id: Product identifier

    Returns:
        Correction result with AI analysis and revised recommendation
    """
    try:
        validate_required_fields(event, ['correction_id', 'product_id'])

        correction_id = event['correction_id']
        product_id = event['product_id']

        timestamp = generate_timestamp()

        # Fetch correction event
        correction = db_client.get_item(CORRECTIONS_TABLE, {'correction_id': correction_id})
        if not correction:
            raise ValueError(f"Correction event {correction_id} not found")

        # Fetch related data
        decision_id = correction['original_decision_id']

        product = db_client.get_item(PRODUCTS_TABLE, {'product_id': product_id})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        decision = db_client.get_item(DECISIONS_TABLE, {'decision_id': decision_id})
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")

        # Build analysis prompt
        prompt = build_analysis_prompt(
            product_data=product,
            decision_data=decision,
            performance_data=correction['performance'],
            deviation_data=correction['deviation']
        )

        # Call Bedrock for AI analysis
        try:
            ai_response = call_bedrock_claude(prompt)
            ai_analysis_source = 'bedrock'
        except Exception as e:
            logger.warning(f"Bedrock call failed, using fallback: {e}")
            ai_response = generate_fallback_correction(decision, correction['performance'])
            ai_analysis_source = 'fallback'

        # Prepare correction record
        correction_update = {
            'status': 'completed',
            'completed_at': timestamp,
            'ai_analysis_source': ai_analysis_source,
            'ai_analysis': ai_response,
            'retry_count': correction.get('retry_count', 0) + 1
        }

        # Update correction record
        db_client.update_item(
            CORRECTIONS_TABLE,
            {'correction_id': correction_id},
            'SET #status = :status, completed_at = :timestamp, '
            'ai_analysis_source = :source, ai_analysis = :analysis, '
            'retry_count = :retry',
            {
                ':status': correction_update['status'],
                ':timestamp': timestamp,
                ':source': ai_analysis_source,
                ':analysis': ai_response,
                ':retry': correction_update['retry_count']
            }
        )

        # If AI provided a revised price, create new decision
        revised_price = ai_response.get('revised_price')
        if revised_price and isinstance(revised_price, (int, float)):
            new_decision_id = f"decision_{product_id}_{timestamp}".replace(':', '-').replace('.', '-')

            new_decision = {
                'decision_id': new_decision_id,
                'product_id': product_id,
                'timestamp': timestamp,
                'input_data': decision['input_data'],
                'output_data': {
                    'recommended_price': revised_price,
                    'predicted_margin': ai_response.get('revised_predicted_margin', decision['output_data']['predicted_margin']),
                    'predicted_sales': ai_response.get('revised_predicted_sales', decision['output_data']['predicted_sales']),
                    'min_viable_price': decision['output_data']['min_viable_price']
                },
                'pricing_strategy': 'ai_corrected',
                'source_correction_id': correction_id,
                'status': 'pending_validation',
                'ai_confidence': ai_response.get('confidence', 'low'),
                'created_at': timestamp
            }

            db_client.put_item(DECISIONS_TABLE, new_decision)

            logger.info(f"Created new AI-corrected decision {new_decision_id}")

            result = {
                'status': STATUS_SUCCESS,
                'correction_id': correction_id,
                'product_id': product_id,
                'ai_analysis_source': ai_analysis_source,
                'analysis': ai_response.get('analysis'),
                'revised_price': revised_price,
                'new_decision_id': new_decision_id,
                'confidence': ai_response.get('confidence'),
                'recommendations': ai_response.get('recommendations', []),
                'timestamp': timestamp
            }
        else:
            result = {
                'status': STATUS_SUCCESS,
                'correction_id': correction_id,
                'product_id': product_id,
                'ai_analysis_source': ai_analysis_source,
                'analysis': ai_response.get('analysis'),
                'revised_price': None,
                'confidence': ai_response.get('confidence', 'low'),
                'recommendations': ai_response.get('recommendations', ['Manual review required']),
                'timestamp': timestamp
            }

        logger.info(f"Correction completed for {correction_id}")

        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }
    except Exception as e:
        logger.exception(f"Error in correction agent: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'CORRECTION_ERROR'
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for correction agent.

    Args:
        event: Lambda event payload
        context: Lambda context

    Returns:
        JSON response with correction result
    """
    logger.info(f"Correction agent invoked with event: {json.dumps(event, default=str)}")

    try:
        # Handle different event sources
        if 'Records' in event:
            # Batch processing
            results = []
            for record in event['Records']:
                if 'body' in record:
                    body = json.loads(record['body'])
                elif 'kinesis' in record:
                    body = json.loads(record['kinesis']['data'])
                else:
                    body = record

                result = run_correction(body)
                results.append(result)

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'processed': len(results),
                    'results': results
                }, default=str)
            }

        elif 'detail' in event:
            # EventBridge event
            result = run_correction(event['detail'])
        else:
            # Direct invocation
            result = run_correction(event)

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