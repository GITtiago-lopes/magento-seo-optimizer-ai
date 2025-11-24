#!/usr/bin/env python
"""
Test updating with extension_attributes included
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

# Fetch current product
print("1. Fetching current product...")
with httpx.Client(timeout=60.0) as client:
    response = client.get(url, headers=headers)

if response.status_code != 200:
    print(f"Error: {response.text}")
    exit(1)

current_product = response.json()
print(f"✓ Fetched: {current_product.get('name')}")

# Try update WITH extension_attributes
print("\n2. Testing update WITH extension_attributes...")
payload_with_ext = {
    "product": {
        "id": current_product.get("id"),
        "sku": SKU,
        "name": current_product.get("name"),
        "attribute_set_id": current_product.get("attribute_set_id"),
        "status": current_product.get("status"),
        "visibility": current_product.get("visibility"),
        "type_id": current_product.get("type_id"),
        "weight": current_product.get("weight"),
        "extension_attributes": current_product.get("extension_attributes", {}),
        "custom_attributes": [
            {"attribute_code": "meta_title", "value": "Updated with EXT"},
            {"attribute_code": "meta_description", "value": "Updated with extension_attributes"},
            {"attribute_code": "meta_keyword", "value": "with, extension, attributes"},
        ]
    }
}

with httpx.Client(timeout=60.0) as client:
    response = client.put(url, headers=headers, json=payload_with_ext)

print(f"Status: {response.status_code}")
if response.status_code < 400:
    print("✓ SUCCESS!")
else:
    print(f"✗ Failed: {response.text[:200]}")

# Try update WITHOUT extension_attributes
print("\n3. Testing update WITHOUT extension_attributes...")
payload_without_ext = {
    "product": {
        "id": current_product.get("id"),
        "sku": SKU,
        "name": current_product.get("name"),
        "attribute_set_id": current_product.get("attribute_set_id"),
        "status": current_product.get("status"),
        "visibility": current_product.get("visibility"),
        "type_id": current_product.get("type_id"),
        "weight": current_product.get("weight"),
        "custom_attributes": [
            {"attribute_code": "meta_title", "value": "Updated without EXT"},
            {"attribute_code": "meta_description", "value": "Updated without extension_attributes"},
            {"attribute_code": "meta_keyword", "value": "without, extension, attributes"},
        ]
    }
}

with httpx.Client(timeout=60.0) as client:
    response = client.put(url, headers=headers, json=payload_without_ext)

print(f"Status: {response.status_code}")
if response.status_code < 400:
    print("✓ SUCCESS!")
else:
    print(f"✗ Failed: {response.text[:200]}")

# Try update WITH only custom_attributes (minimal)
print("\n4. Testing update MINIMAL (only custom_attributes)...")
payload_minimal = {
    "product": {
        "custom_attributes": [
            {"attribute_code": "meta_title", "value": "Updated minimal"},
            {"attribute_code": "meta_description", "value": "Minimal update"},
            {"attribute_code": "meta_keyword", "value": "minimal"},
        ]
    }
}

with httpx.Client(timeout=60.0) as client:
    response = client.put(url, headers=headers, json=payload_minimal)

print(f"Status: {response.status_code}")
if response.status_code < 400:
    print("✓ SUCCESS!")
else:
    print(f"✗ Failed: {response.text[:200]}")
