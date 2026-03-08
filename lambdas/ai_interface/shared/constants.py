"""
Constants and configuration for Autonomous Pricing Engine.
"""

import os

# DynamoDB Table Names (from environment variables)
PRODUCTS_TABLE = os.environ.get('PRODUCTS_TABLE', 'products')
DECISIONS_TABLE = os.environ.get('DECISIONS_TABLE', 'pricing_decisions')
CORRECTIONS_TABLE = os.environ.get('CORRECTIONS_TABLE', 'price_corrections')
CHAT_HISTORY_TABLE = os.environ.get('CHAT_HISTORY_TABLE', 'autonomous-pricing-chat-history')

# Pricing Constants
MIN_MARGIN_PERCENT = float(os.environ.get('MIN_MARGIN_PERCENT', '5.0'))  # Minimum 5% margin
MAX_PRICE_DROP_PERCENT = float(os.environ.get('MAX_PRICE_DROP_PERCENT', '25.0'))  # Max 25% drop
DEVIATION_THRESHOLD_PERCENT = float(os.environ.get('DEVIATION_THRESHOLD_PERCENT', '20.0'))  # 20% deviation

# Bedrock Configuration
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', '')
BEDROCK_REGION = os.environ.get('BEDROCK_REGION', 'us-east-1')
BEDROCK_GUARDRAIL_ID = os.environ.get('BEDROCK_GUARDRAIL_ID', '')
BEDROCK_GUARDRAIL_VERSION = os.environ.get('BEDROCK_GUARDRAIL_VERSION', '')

# Response Status Codes
STATUS_SUCCESS = 'SUCCESS'
STATUS_FAILED = 'FAILED'
STATUS_VALID = 'VALID'
STATUS_INVALID = 'INVALID'
STATUS_CORRECTION_TRIGGERED = 'CORRECTION_TRIGGERED'

# Event Sources
EVENT_SOURCE_MARKET = 'market_processor'
EVENT_SOURCE_PRICING = 'pricing_engine'
EVENT_SOURCE_GUARDRAIL = 'guardrail_executor'
EVENT_SOURCE_MONITORING = 'monitoring_agent'
EVENT_SOURCE_CORRECTION = 'correction_agent'
