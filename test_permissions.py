#!/usr/bin/env python
"""
Test if we can update ANY attribute
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

# Try updating just the description (non-SEO field)
print("1. Testing update of DESCRIPTION field (non-SEO)...")
payload = {
    "product": {
        "description": "Test updated description"
    }
}

with httpx.Client(timeout=60.0) as client:
    response = client.put(url, headers=headers, json=payload)

print(f"Status: {response.status_code}")
if response.status_code < 400:
    print("✓ Can update description")
else:
    print(f"✗ Cannot update description: {response.text[:150]}")

# Try updating short description
print("\n2. Testing update of SHORT_DESCRIPTION field (non-SEO)...")
payload = {
    "product": {
        "short_description": "Test updated short description"
    }
}

with httpx.Client(timeout=60.0) as client:
    response = client.put(url, headers=headers, json=payload)

print(f"Status: {response.status_code}")
if response.status_code < 400:
    print("✓ Can update short_description")
else:
    print(f"✗ Cannot update short_description: {response.text[:150]}")

# Try updating name
print("\n3. Testing update of NAME field (core field)...")
payload = {
    "product": {
        "name": "Notebook ASUS X515JA-BR3932W Cinza"
    }
}

with httpx.Client(timeout=60.0) as client:
    response = client.put(url, headers=headers, json=payload)

print(f"Status: {response.status_code}")
if response.status_code < 400:
    print("✓ Can update name")
else:
    print(f"✗ Cannot update name: {response.text[:150]}")

# Try updating a custom attribute that's simple
print("\n4. Testing update of SIMPLE custom_attribute (non-SEO)...")
payload = {
    "product": {
        "custom_attributes": [
            {"attribute_code": "url_key", "value": "notebook-asus-x515ja-br3932w-cinza"}
        ]
    }
}

with httpx.Client(timeout=60.0) as client:
    response = client.put(url, headers=headers, json=payload)

print(f"Status: {response.status_code}")
if response.status_code < 400:
    print("✓ Can update custom_attributes")
else:
    print(f"✗ Cannot update custom_attributes: {response.text[:150]}")
