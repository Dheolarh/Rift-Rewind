"""
AWS client initialization utilities
"""

import boto3
import json
from typing import Optional, Union, Dict, Any
from .constants import AWS_REGION, S3_BUCKET_NAME


# Singleton clients
_s3_client = None
_bedrock_client = None
_sagemaker_client = None


def get_s3_client():
    """
    Get or create S3 client (singleton pattern).
    
    Returns:
        boto3 S3 client
    """
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client('s3', region_name=AWS_REGION)
    return _s3_client


def get_bedrock_client():
    """
    Get or create Bedrock Runtime client (singleton pattern).
    
    Returns:
        boto3 Bedrock Runtime client
    """
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION
        )
    return _bedrock_client


def get_sagemaker_client():
    """
    Get or create SageMaker Runtime client (singleton pattern).
    
    Returns:
        boto3 SageMaker Runtime client
    """
    global _sagemaker_client
    if _sagemaker_client is None:
        _sagemaker_client = boto3.client(
            service_name='sagemaker-runtime',
            region_name=AWS_REGION
        )
    return _sagemaker_client


def upload_to_s3(key: str, data: Union[str, Dict[str, Any]], content_type: str = 'application/json') -> bool:
    """
    Upload data to S3 bucket.
    
    Args:
        key: S3 object key (path)
        data: Data to upload (string or dict - dicts will be converted to JSON)
        content_type: Content type header
        
    Returns:
        True if successful, False otherwise
    """
    try:
        s3_client = get_s3_client()
        
        # Convert dict to JSON string if needed
        if isinstance(data, dict):
            data = json.dumps(data, indent=2)
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
            Body=data.encode('utf-8'),
            ContentType=content_type
        )
        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False


def download_from_s3(key: str) -> Optional[str]:
    """
    Download data from S3 bucket.
    
    Args:
        key: S3 object key (path)
        
    Returns:
        Downloaded data as string, or None if error
    """
    try:
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading from S3: {e}")
        return None


def check_s3_object_exists(key: str) -> bool:
    """
    Check if an object exists in S3.
    
    Args:
        key: S3 object key (path)
        
    Returns:
        True if exists, False otherwise
    """
    try:
        s3_client = get_s3_client()
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        return True
    except:
        return False
