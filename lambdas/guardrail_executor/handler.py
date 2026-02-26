"""
Guardrail Executor Lambda Handler

Validates pricing decisions against business rules and safety constraints.
Prevents invalid or risky price changes from being applied.
"""

import json
from typing import Any, Dict, List
import sys
import os

# Add shared module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    DynamoDBClient,
    setup_logger,
    validate_required_fields,
    generate_timestamp,
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    MIN_MARGIN_PERCENT,
    MAX_PRICE_DROP_PERCENT,
    STATUS_SUCCESS,
    STATUS_FAILED,
    STATUS_VALID,
    STATUS_INVALID
)

logger = setup_logger(__name__)
db_client = DynamoDBClient()


class ValidationError(Exception):
    """Custom exception for validation failures."""
    def __init__(self, message: str, violation_type: str):
        super().__init__(message)
        self.violation_type = violation_type


def validate_margin_floor(
    recommended_price: float,
    cost_price: float,
    gst_percent: float,
    min_margin_percent: float = MIN_MARGIN_PERCENT
) -> Dict[str, Any]:
    """
    Validate that recommended price maintains minimum margin.

    Args:
        recommended_price: Proposed price
        cost_price: Product cost
        gst_percent: GST percentage
        min_margin_percent: Required minimum margin

    Returns:
        Validation result with margin details

    Raises:
        ValidationError: If margin is below minimum
    """
    cost_with_gst = cost_price * (1 + gst_percent / 100)
    actual_margin = ((recommended_price - cost_with_gst) / recommended_price) * 100
    actual_margin = round(actual_margin, 2)

    if actual_margin < min_margin_percent:
        raise ValidationError(
            f"Margin {actual_margin}% below minimum {min_margin_percent}%",
            violation_type='MARGIN_FLOOR_VIOLATION'
        )

    return {
        'validation': 'margin_floor',
        'status': 'PASS',
        'actual_margin': actual_margin,
        'min_margin': min_margin_percent,
        'margin_buffer': round(actual_margin - min_margin_percent, 2)
    }


def validate_price_above_cost(
    recommended_price: float,
    cost_price: float,
    gst_percent: float
) -> Dict[str, Any]:
    """
    Ensure price is above cost + GST (absolute minimum).

    Args:
        recommended_price: Proposed price
        cost_price: Product cost
        gst_percent: GST percentage

    Returns:
        Validation result

    Raises:
        ValidationError: If price is at or below cost+GST
    """
    cost_with_gst = cost_price * (1 + gst_percent / 100)

    if recommended_price <= cost_with_gst:
        raise ValidationError(
            f"Price {recommended_price} at or below cost+GST {cost_with_gst}",
            violation_type='PRICE_BELOW_COST'
        )

    return {
        'validation': 'price_above_cost',
        'status': 'PASS',
        'recommended_price': recommended_price,
        'cost_with_gst': round(cost_with_gst, 2),
        'buffer': round(recommended_price - cost_with_gst, 2)
    }


def validate_price_drop_limit(
    recommended_price: float,
    current_price: float,
    max_drop_percent: float = MAX_PRICE_DROP_PERCENT
) -> Dict[str, Any]:
    """
    Prevent extreme price drops (>25% by default).

    Args:
        recommended_price: Proposed price
        current_price: Current selling price
        max_drop_percent: Maximum allowed drop percentage

    Returns:
        Validation result

    Raises:
        ValidationError: If price drop exceeds limit
    """
    if current_price <= 0:
        # No current price, skip this validation
        return {
            'validation': 'price_drop_limit',
            'status': 'SKIP',
            'reason': 'No current price to compare'
        }

    price_change = recommended_price - current_price
    drop_percent = abs((price_change / current_price) * 100)

    if price_change < 0 and drop_percent > max_drop_percent:
        raise ValidationError(
            f"Price drop {drop_percent:.2f}% exceeds maximum {max_drop_percent}%",
            violation_type='EXCESSIVE_PRICE_DROP'
        )

    return {
        'validation': 'price_drop_limit',
        'status': 'PASS',
        'current_price': current_price,
        'recommended_price': recommended_price,
        'change_percent': round(drop_percent, 2),
        'max_allowed': max_drop_percent
    }


def run_validation_checks(
    decision: Dict[str, Any],
    product: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run all validation checks on a pricing decision.

    Args:
        decision: Pricing decision record
        product: Product record

    Returns:
        Validation results with all checks
    """
    validations = []

    recommended_price = decision['output_data']['recommended_price']
    cost_price = decision['input_data']['cost_price']
    gst_percent = decision['input_data']['gst_percent']
    current_price = decision['input_data'].get('current_price', 0)

    # Run all validations
    try:
        validations.append(validate_margin_floor(
            recommended_price, cost_price, gst_percent
        ))
    except ValidationError as e:
        validations.append({
            'validation': 'margin_floor',
            'status': 'FAIL',
            'error': str(e),
            'violation_type': e.violation_type
        })
        raise

    try:
        validations.append(validate_price_above_cost(
            recommended_price, cost_price, gst_percent
        ))
    except ValidationError as e:
        validations.append({
            'validation': 'price_above_cost',
            'status': 'FAIL',
            'error': str(e),
            'violation_type': e.violation_type
        })
        raise

    try:
        validations.append(validate_price_drop_limit(
            recommended_price, current_price
        ))
    except ValidationError as e:
        validations.append({
            'validation': 'price_drop_limit',
            'status': 'FAIL',
            'error': str(e),
            'violation_type': e.violation_type
        })
        raise

    return {
        'all_passed': True,
        'validations': validations
    }


def execute_guardrails(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute guardrail validation for a pricing decision.

    Args:
        event: Guardrail event containing:
            - decision_id: ID of the pricing decision to validate
            - product_id: Product identifier
            - auto_apply: Whether to apply price if valid (default: True)

    Returns:
        Validation result and action taken
    """
    try:
        validate_required_fields(event, ['decision_id', 'product_id'])

        decision_id = event['decision_id']
        product_id = event['product_id']
        auto_apply = event.get('auto_apply', True)

        timestamp = generate_timestamp()

        # Fetch decision and product records
        decision = db_client.get_item(DECISIONS_TABLE, {'decision_id': decision_id})
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")

        product = db_client.get_item(PRODUCTS_TABLE, {'product_id': product_id})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Run validation checks
        try:
            validation_result = run_validation_checks(decision, product)

            # All validations passed
            result_status = STATUS_VALID
            decision_status = 'approved'

            # Update decision status
            db_client.update_item(
                DECISIONS_TABLE,
                {'decision_id': decision_id},
                'SET #status = :status, validated_at = :timestamp, validations = :validations',
                {
                    ':status': decision_status,
                    ':timestamp': timestamp,
                    ':validations': validation_result['validations']
                }
            )

            # Apply price if auto_apply is enabled
            if auto_apply:
                new_price = decision['output_data']['recommended_price']

                db_client.update_item(
                    PRODUCTS_TABLE,
                    {'product_id': product_id},
                    'SET current_price = :price, price_updated_at = :timestamp, '
                    'last_decision_id = :decision_id, updated_at = :timestamp',
                    {
                        ':price': new_price,
                        ':timestamp': timestamp,
                        ':decision_id': decision_id
                    }
                )

                applied_action = 'price_applied'
                logger.info(f"Applied new price {new_price} to product {product_id}")
            else:
                applied_action = 'validation_only'

            logger.info(f"Guardrail validation passed for decision {decision_id}")

            return {
                'status': STATUS_SUCCESS,
                'validation_status': STATUS_VALID,
                'decision_id': decision_id,
                'product_id': product_id,
                'action': applied_action,
                'new_price': decision['output_data']['recommended_price'] if auto_apply else None,
                'validations': validation_result['validations'],
                'timestamp': timestamp
            }

        except ValidationError as e:
            # Validation failed
            result_status = STATUS_INVALID
            decision_status = 'rejected'

            # Update decision status
            db_client.update_item(
                DECISIONS_TABLE,
                {'decision_id': decision_id},
                'SET #status = :status, validated_at = :timestamp, '
                'rejection_reason = :reason, violation_type = :violation',
                {
                    ':status': decision_status,
                    ':timestamp': timestamp,
                    ':reason': str(e),
                    ':violation': e.violation_type
                }
            )

            logger.warning(f"Guardrail validation failed for decision {decision_id}: {e}")

            return {
                'status': STATUS_SUCCESS,
                'validation_status': STATUS_INVALID,
                'decision_id': decision_id,
                'product_id': product_id,
                'action': 'rejected',
                'rejection_reason': str(e),
                'violation_type': e.violation_type,
                'timestamp': timestamp
            }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }
    except Exception as e:
        logger.exception(f"Error in guardrail executor: {e}")
        return {
            'status': STATUS_FAILED,
            'error': str(e),
            'error_type': 'GUARDRAIL_ERROR'
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for guardrail executor.

    Args:
        event: Lambda event payload
        context: Lambda context

    Returns:
        JSON response with validation result
    """
    logger.info(f"Guardrail executor invoked with event: {json.dumps(event, default=str)}")

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

                result = execute_guardrails(body)
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
            result = execute_guardrails(event['detail'])
        else:
            # Direct invocation
            result = execute_guardrails(event)

        status_code = 200 if result['status'] == STATUS_SUCCESS else 400
        return {
            'statusCode': status_code,
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