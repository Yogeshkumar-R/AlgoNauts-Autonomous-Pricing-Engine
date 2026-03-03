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
from langsmith import traceable

# Add shared module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    MAX_PRICE_DROP_PERCENT,
    MIN_MARGIN_PERCENT,
    STATUS_SUCCESS,
    STATUS_FAILED
)

logger = setup_logger(__name__)
db_client = DynamoDBClient()

# Initialize Bedrock client (lazy)
_bedrock_client = None
MAX_BEDROCK_TEXT_CHARS = int(os.environ.get('MAX_BEDROCK_TEXT_CHARS', '8000'))


def get_bedrock_client():
    """Get or create Bedrock runtime client."""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=BEDROCK_REGION
        )
    return _bedrock_client


def extract_json_object(text: str) -> str:
    """Extract first JSON object block from model text output."""
    if not isinstance(text, str):
        return "{}"
    cleaned = text.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    if cleaned.startswith('```'):
        cleaned = cleaned[3:]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return "{}"
    return cleaned[start:end + 1]


def normalize_ai_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize AI response shape."""
    confidence = str(payload.get('confidence', 'low')).lower()
    if confidence not in {'high', 'medium', 'low'}:
        confidence = 'low'

    factors = payload.get('factors', [])
    if not isinstance(factors, list):
        factors = [str(factors)]
    factors = [str(x)[:120] for x in factors][:6]

    recs = payload.get('recommendations', [])
    if not isinstance(recs, list):
        recs = [str(recs)]
    recs = [str(x)[:200] for x in recs][:6]

    revised_price = payload.get('revised_price')
    if isinstance(revised_price, (int, float)):
        revised_price = round(float(revised_price), 2)
    else:
        revised_price = None

    revised_predicted_sales = payload.get('revised_predicted_sales')
    if isinstance(revised_predicted_sales, (int, float)):
        revised_predicted_sales = max(0, int(revised_predicted_sales))
    else:
        revised_predicted_sales = None

    revised_predicted_margin = payload.get('revised_predicted_margin')
    if isinstance(revised_predicted_margin, (int, float)):
        revised_predicted_margin = round(float(revised_predicted_margin), 2)
    else:
        revised_predicted_margin = None

    return {
        "analysis": str(payload.get('analysis', 'No analysis provided'))[:1000],
        "factors": factors,
        "revised_price": revised_price,
        "revised_predicted_sales": revised_predicted_sales,
        "revised_predicted_margin": revised_predicted_margin,
        "confidence": confidence,
        "explanation": str(payload.get('explanation', 'No explanation provided'))[:2000],
        "recommendations": recs or ["Manual review required"]
    }


def apply_price_guardrails(ai_response: Dict[str, Any], decision_data: Dict[str, Any]) -> Dict[str, Any]:
    """Constrain revised price to configured pricing guardrails."""
    revised_price = ai_response.get('revised_price')
    if revised_price is None:
        return ai_response

    input_data = decision_data.get('input_data', {})
    current_price = float(input_data.get('current_price', 0) or 0)
    cost_price = float(input_data.get('cost_price', 0) or 0)
    gst_percent = float(input_data.get('gst_percent', 18) or 18)

    min_floor = cost_price * (1 + gst_percent / 100) * (1 + MIN_MARGIN_PERCENT / 100)
    min_drop_price = current_price * (1 - MAX_PRICE_DROP_PERCENT / 100) if current_price > 0 else revised_price
    max_rise_price = current_price * 1.5 if current_price > 0 else revised_price

    guarded = min(revised_price, max_rise_price)
    guarded = max(guarded, min_floor, min_drop_price)
    guarded = round(guarded, 2)

    if guarded != revised_price:
        ai_response["analysis"] = f"{ai_response.get('analysis', '')} Guardrail-adjusted revised price.".strip()
    ai_response["revised_price"] = guarded
    return ai_response


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


@traceable(
    name="bedrock-claude-correction",
    tags=["bedrock", "correction", "pricing"],
    metadata={"model": "claude-haiku-4-5"}
)
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

        logger.info(f"Calling Bedrock model: {BEDROCK_MODEL_ID}")

        response = client.converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{
                "text": (
                    "You are a pricing correction model. Return only valid JSON with requested keys. "
                    "Do not output markdown or prose outside JSON."
                )
            }],
            messages=[{
                "role": "user",
                "content": [{"text": prompt}]
            }],
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.2
            }
        )
        content = response.get('output', {}).get('message', {}).get('content', [])
        text_response = content[0].get('text', '{}') if content else '{}'
        text_response = text_response[:MAX_BEDROCK_TEXT_CHARS]
        parsed_response = json.loads(extract_json_object(text_response))
        parsed_response = normalize_ai_response(parsed_response)

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
            ai_response = apply_price_guardrails(ai_response, decision)
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

        # Update correction record with completed status (fix: #status reserved word)
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
            },
            expression_attribute_names={'#status': 'status'}
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

    Accepts:
    - Step Functions (_sf_mode: true) — returns clean dict with ai_revised_price
    - EventBridge / Direct — returns HTTP response
    """
    logger.info(f"Correction agent invoked: {json.dumps(event, default=str)[:300]}")

    sf_mode = event.get('_sf_mode', False)

    try:
        if 'detail' in event:
            result = run_correction(event['detail'])
        else:
            result = run_correction(event)

        if sf_mode:
            if result.get('status') == STATUS_FAILED:
                raise Exception(result.get('error', 'correction_agent failed'))
            return result

        return {
            'statusCode': 200 if result['status'] == STATUS_SUCCESS else 400,
            'body': json.dumps(result, default=str)
        }

    except Exception as e:
        logger.exception(f"Lambda handler error: {e}")
        if sf_mode:
            raise
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': STATUS_FAILED,
                'error': str(e),
                'error_type': 'HANDLER_ERROR'
            })
        }
