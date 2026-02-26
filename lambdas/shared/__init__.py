"""
Shared utilities for Autonomous Pricing Engine Lambda functions.
"""

from .dynamodb import DynamoDBClient
from .utils import setup_logger, get_env_var, validate_required_fields
from .constants import (
    PRODUCTS_TABLE,
    DECISIONS_TABLE,
    CORRECTIONS_TABLE,
    MIN_MARGIN_PERCENT,
    MAX_PRICE_DROP_PERCENT,
    DEVIATION_THRESHOLD_PERCENT
)

__all__ = [
    'DynamoDBClient',
    'setup_logger',
    'get_env_var',
    'validate_required_fields',
    'PRODUCTS_TABLE',
    'DECISIONS_TABLE',
    'CORRECTIONS_TABLE',
    'MIN_MARGIN_PERCENT',
    'MAX_PRICE_DROP_PERCENT',
    'DEVIATION_THRESHOLD_PERCENT'
]