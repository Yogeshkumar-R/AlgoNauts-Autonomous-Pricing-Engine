"""
DynamoDB client wrapper for Autonomous Pricing Engine.
"""

import boto3
from botocore.exceptions import ClientError
from typing import Any, Dict, List, Optional
from .utils import setup_logger

logger = setup_logger(__name__)


import json
from decimal import Decimal

def _from_decimal(obj):
    if isinstance(obj, Decimal):
        # Convert Decimal to int if it's a whole number, else float
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _from_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_from_decimal(v) for v in obj]
    return obj

def _to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: _to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_decimal(v) for v in obj]
    return obj

class DynamoDBClient:
    """
    Wrapper class for DynamoDB operations.
    Handles connection management and common CRUD operations.
    """

    def __init__(self, region: Optional[str] = None):
        """
        Initialize DynamoDB client.

        Args:
            region: AWS region (defaults to environment or us-east-1)
        """
        self.region = region or boto3.session.Session().region_name or 'us-east-1'
        self._client = None
        self._resource = None

    @property
    def client(self):
        """Lazy initialization of DynamoDB client."""
        if self._client is None:
            self._client = boto3.client('dynamodb', region_name=self.region)
        return self._client

    @property
    def resource(self):
        """Lazy initialization of DynamoDB resource."""
        if self._resource is None:
            self._resource = boto3.resource('dynamodb', region_name=self.region)
        return self._resource

    def get_table(self, table_name: str):
        """
        Get DynamoDB table resource.

        Args:
            table_name: Name of the table

        Returns:
            DynamoDB Table resource
        """
        return self.resource.Table(table_name)

    def get_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        consistent_read: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get item from DynamoDB table.

        Args:
            table_name: Name of the table
            key: Primary key dict (e.g., {'product_id': '123'})
            consistent_read: Whether to use consistent read

        Returns:
            Item dict or None if not found
        """
        try:
            table = self.get_table(table_name)
            response = table.get_item(
                Key=key,
                ConsistentRead=consistent_read
            )
            item = response.get('Item')
            logger.info(f"Retrieved item from {table_name}: {key}")
            return _from_decimal(item) if item is not None else None
        except ClientError as e:
            logger.error(f"Error getting item from {table_name}: {e}")
            raise

    def put_item(
        self,
        table_name: str,
        item: Dict[str, Any],
        condition_expression: Optional[str] = None
    ) -> bool:
        """
        Put item into DynamoDB table.

        Args:
            table_name: Name of the table
            item: Item dictionary to insert
            condition_expression: Optional condition expression

        Returns:
            True if successful
        """
        try:
            table = self.get_table(table_name)
            kwargs = {'Item': _to_decimal(item)}
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression

            table.put_item(**kwargs)
            logger.info(f"Put item into {table_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"Conditional check failed for {table_name}")
            else:
                logger.error(f"Error putting item to {table_name}: {e}")
            raise

    def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_values: Dict[str, Any],
        return_values: str = 'UPDATED_NEW',
        expression_attribute_names: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update item in DynamoDB table.

        Args:
            table_name: Name of the table
            key: Primary key dict
            update_expression: Update expression (e.g., 'SET #status = :status')
            expression_values: Expression attribute values
            return_values: What to return ('UPDATED_NEW', 'ALL_NEW', etc.)
            expression_attribute_names: Optional dict mapping placeholders to reserved words
                e.g. {'#status': 'status'} when 'status' is a reserved word

        Returns:
            Updated attributes or None
        """
        try:
            table = self.get_table(table_name)
            kwargs = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': _to_decimal(expression_values),
                'ReturnValues': return_values
            }
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names

            response = table.update_item(**kwargs)
            logger.info(f"Updated item in {table_name}: {key}")
            attributes = response.get('Attributes')
            return _from_decimal(attributes) if attributes else None
        except ClientError as e:
            logger.error(f"Error updating item in {table_name}: {e}")
            raise


    def query(
        self,
        table_name: str,
        key_condition: str,
        expression_values: Dict[str, Any],
        index_name: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query DynamoDB table.

        Args:
            table_name: Name of the table
            key_condition: Key condition expression
            expression_values: Expression attribute values
            index_name: Optional index name
            limit: Optional limit on items returned

        Returns:
            List of matching items
        """
        try:
            table = self.get_table(table_name)
            kwargs = {
                'KeyConditionExpression': key_condition,
                'ExpressionAttributeValues': _to_decimal(expression_values)
            }
            if index_name:
                kwargs['IndexName'] = index_name
            if limit:
                kwargs['Limit'] = limit

            response = table.query(**kwargs)
            items = response.get('Items', [])
            logger.info(f"Query returned {len(items)} items from {table_name}")
            return _from_decimal(items)
        except ClientError as e:
            logger.error(f"Error querying {table_name}: {e}")
            raise

    def scan(
        self,
        table_name: str,
        filter_expression: Optional[str] = None,
        expression_values: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan DynamoDB table.

        Args:
            table_name: Name of the table
            filter_expression: Optional filter expression
            expression_values: Optional expression attribute values
            limit: Optional limit on items returned

        Returns:
            List of matching items
        """
        try:
            table = self.get_table(table_name)
            kwargs = {}
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            if expression_values:
                kwargs['ExpressionAttributeValues'] = expression_values
            if limit:
                kwargs['Limit'] = limit

            response = table.scan(**kwargs)
            items = response.get('Items', [])
            logger.info(f"Scan returned {len(items)} items from {table_name}")
            return _from_decimal(items)
        except ClientError as e:
            logger.error(f"Error scanning {table_name}: {e}")
            raise

    def batch_write(
        self,
        table_name: str,
        items: List[Dict[str, Any]]
    ) -> bool:
        """
        Batch write items to DynamoDB table.

        Args:
            table_name: Name of the table
            items: List of item dictionaries to write

        Returns:
            True if successful
        """
        try:
            table = self.get_table(table_name)
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=_to_decimal(item))
            logger.info(f"Batch wrote {len(items)} items to {table_name}")
            return True
        except ClientError as e:
            logger.error(f"Error batch writing to {table_name}: {e}")
            raise