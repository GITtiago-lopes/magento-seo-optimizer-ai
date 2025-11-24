#!/usr/bin/env python
"""
Test PATCH vs PUT for SEO update
"""
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

MAGENTO_BASE_URL = os.getenv("MAGENTO_BASE_URL", "https://brstage.store.asus.com")
MAGENTO_API_TOKEN = os.getenv("MAGENTO_API_TOKEN")
SKU = "90NB0SR1-M02FC0"

headers = {
    "Authorization": f"Bearer {MAGENTO_API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

url = f"{MAGENTO_BASE_URL}/rest/V1/products/{SKU}"

payload = {
    "product": {
        "custom_attributes": [
            {"attribute_code": "meta_title", "value": "Test PATCH Title"},
            {"attribute_code": "meta_description", "value": "Test PATCH Description"},
            {"attribute_code": "meta_keyword", "value": "test, patch"},
        ]
    }
}

print("Testing PATCH request...")
print(json.dumps(payload, indent=2))

try:
    with httpx.Client(timeout=60.0) as client:
        response = client.patch(url, headers=headers, json=payload)
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code < 400:
        print("\n✓ SUCCESS with PATCH!")
    else:
        print("\n✗ PATCH failed")
        
except Exception as e:
    print(f"Error: {e}")
