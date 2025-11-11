"""
AWS client initialization utilities
"""

import boto3
import json
import os
from pathlib import Path
from typing import Optional, Union, Dict, Any
from .constants import AWS_DEFAULT_REGION, S3_BUCKET_NAME


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
        _s3_client = boto3.client('s3', region_name=AWS_DEFAULT_REGION)
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
            region_name=AWS_DEFAULT_REGION
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
            region_name=AWS_DEFAULT_REGION
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
        # Fallback for local development: store in .local_s3 folder when S3 is unavailable
        try:
            local_root = Path(__file__).resolve().parents[1] / '.local_s3'
            local_path = local_root / key
            local_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, bytes):
                body = data
            else:
                body = data.encode('utf-8') if isinstance(data, str) else json.dumps(data, indent=2).encode('utf-8')
            with open(local_path, 'wb') as f:
                f.write(body)
            return True
        except Exception:
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
        # Fallback: read from local .local_s3 folder
        try:
            local_root = Path(__file__).resolve().parents[1] / '.local_s3'
            local_path = local_root / key
            if not local_path.exists():
                return None
            with open(local_path, 'rb') as f:
                return f.read().decode('utf-8')
        except Exception:
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
        # Fallback: check local .local_s3
        try:
            local_root = Path(__file__).resolve().parents[1] / '.local_s3'
            local_path = local_root / key
            return local_path.exists()
        except Exception:
            return False
