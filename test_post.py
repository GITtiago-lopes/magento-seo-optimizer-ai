#!/usr/bin/env python
"""
Try POST instead of PUT
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

url = f"{MAGENTO_BASE_URL}/rest/V1/products"

payload = {
    "product": {
        "sku": SKU,
        "custom_attributes": [
            {"attribute_code": "meta_title", "value": "Updated via POST"},
            {"attribute_code": "meta_description", "value": "Testing POST"},
            {"attribute_code": "meta_keyword", "value": "post, test"},
        ]
    }
}

print("Testing POST method...")
with httpx.Client(timeout=60.0) as client:
    response = client.post(url, headers=headers, json=payload)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:300]}")

if response.status_code < 400:
    print("\n✓ SUCCESS with POST!")
else:
    print("\n✗ POST also failed")
