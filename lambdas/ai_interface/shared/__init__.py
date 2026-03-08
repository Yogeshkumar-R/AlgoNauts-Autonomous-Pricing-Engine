"""
Shared utilities for Autonomous Pricing Engine Lambda functions.
"""

from .dynamodb import DynamoDBClient
from .utils import (
    setup_logger,
    get_env_var,
    validate_required_fields,
    generate_timestamp,
    generate_decision_id,
    safe_float,
)
from .constants import (
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    CORRECTIONS_TABLE,
    CHAT_HISTORY_TABLE,
    MIN_MARGIN_PERCENT,
    MAX_PRICE_DROP_PERCENT,
    DEVIATION_THRESHOLD_PERCENT,
    BEDROCK_MODEL_ID,
    BEDROCK_REGION,
    BEDROCK_GUARDRAIL_ID,
    BEDROCK_GUARDRAIL_VERSION,
    STATUS_SUCCESS,
    STATUS_FAILED,
    STATUS_VALID,
    STATUS_INVALID,
    STATUS_CORRECTION_TRIGGERED,
    EVENT_SOURCE_MARKET,
    EVENT_SOURCE_PRICING,
    EVENT_SOURCE_GUARDRAIL,
    EVENT_SOURCE_MONITORING,
    EVENT_SOURCE_CORRECTION,
)

__all__ = [
    # Clients
    'DynamoDBClient',
    # Utils
    'setup_logger',
    'get_env_var',
    'validate_required_fields',
    'generate_timestamp',
    'generate_decision_id',
    'safe_float',
    # Table names
    'PRODUCTS_TABLE',
    'DECISIONS_TABLE',
    'CORRECTIONS_TABLE',
    'CHAT_HISTORY_TABLE',
    # Pricing constants
    'MIN_MARGIN_PERCENT',
    'MAX_PRICE_DROP_PERCENT',
    'DEVIATION_THRESHOLD_PERCENT',
    # Bedrock
    'BEDROCK_MODEL_ID',
    'BEDROCK_REGION',
    'BEDROCK_GUARDRAIL_ID',
    'BEDROCK_GUARDRAIL_VERSION',
    # Statuses
    'STATUS_SUCCESS',
    'STATUS_FAILED',
    'STATUS_VALID',
    'STATUS_INVALID',
    'STATUS_CORRECTION_TRIGGERED',
    # Event sources
    'EVENT_SOURCE_MARKET',
    'EVENT_SOURCE_PRICING',
    'EVENT_SOURCE_GUARDRAIL',
    'EVENT_SOURCE_MONITORING',
    'EVENT_SOURCE_CORRECTION',
]
