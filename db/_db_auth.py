import boto3
import json
from codecs import decode

def _decode_keys(string):
    """Decode a string from rot13"""
    return decode(string, 'rot-13')

def _load_credentials():
    """Load credentials from a JSON file"""
    with open('db/.aws/credentials.json', 'r') as f:
        aws_access_key_id, aws_secret_access_key, region_name = map(_decode_keys, list(json.load(f).values()))
        return {'aws_access_key_id': aws_access_key_id, 'aws_secret_access_key': aws_secret_access_key, 'region_name': region_name}

def get_db():
    """Get a DynamoDB resource"""
    keys = _load_credentials()
    return boto3.resource('dynamodb', **keys)