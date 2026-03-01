"""
Utility functions for Autonomous Pricing Engine.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime


def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger with standard formatting.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Get environment variable with optional default.

    Args:
        key: Environment variable name
        default: Default value if not set

    Returns:
        Environment variable value

    Raises:
        ValueError: If variable not set and no default provided
    """
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Required environment variable '{key}' not set")
    return value


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that all required fields are present in data.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Raises:
        ValueError: If any required field is missing
    """
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def generate_timestamp() -> str:
    """Generate ISO format timestamp."""
    return datetime.utcnow().isoformat()


def generate_decision_id(product_id: str, timestamp: str) -> str:
    """Generate unique decision ID."""
    return f"decision_{product_id}_{timestamp}".replace(':', '-').replace('.', '-')


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default