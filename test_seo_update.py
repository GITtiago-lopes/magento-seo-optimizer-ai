#!/usr/bin/env python
"""
Test script to debug SEO update issues
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

print("=" * 80)
print(f"Testing Magento API Update for SKU: {SKU}")
print("=" * 80)

# Step 1: Fetch product
print("\n1. FETCHING PRODUCT...")
url = f"{MAGENTO_BASE_URL}/rest/V1/products/{SKU}"
with httpx.Client(timeout=60.0) as client:
    response = client.get(url, headers=headers)
    
print(f"Status: {response.status_code}")
if response.status_code == 200:
    product = response.json()
    print(f"Product Name: {product.get('name')}")
    
    # Show existing SEO attributes
    print("\nExisting SEO Attributes:")
    for attr in product.get("custom_attributes", []):
        if attr.get("attribute_code") in ["meta_title", "meta_description", "meta_keyword"]:
            print(f"  {attr.get('attribute_code')}: {attr.get('value')}")
else:
    print(f"Error: {response.text}")
    exit(1)

# Step 2: Try minimal update
print("\n2. TESTING MINIMAL UPDATE WITH ONLY SEO ATTRIBUTES...")
payload = {
    "product": {
        "custom_attributes": [
            {"attribute_code": "meta_title", "value": "Test Title Updated"},
            {"attribute_code": "meta_description", "value": "Test Description Updated"},
            {"attribute_code": "meta_keyword", "value": "test, keywords, updated"},
        ]
    }
}

print(f"\nPayload:")
print(json.dumps(payload, indent=2, ensure_ascii=False))

with httpx.Client(timeout=60.0) as client:
    response = client.put(url, headers=headers, json=payload)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code < 400:
    print("\n✓ SUCCESS! SEO attributes updated.")
else:
    print("\n✗ FAILED! Trying alternative approach...")
    
    # Step 3: Try with core product fields
    print("\n3. TESTING UPDATE WITH CORE PRODUCT FIELDS...")
    payload_with_core = {
        "product": {
            "id": product.get("id"),
            "sku": SKU,
            "name": product.get("name"),
            "attribute_set_id": product.get("attribute_set_id"),
            "status": product.get("status"),
            "visibility": product.get("visibility"),
            "type_id": product.get("type_id"),
            "custom_attributes": [
                {"attribute_code": "meta_title", "value": "Test Title Updated v2"},
                {"attribute_code": "meta_description", "value": "Test Description Updated v2"},
                {"attribute_code": "meta_keyword", "value": "test, keywords, updated, v2"},
            ]
        }
    }
    
    print(f"\nPayload (showing structure only):")
    print(f"  id: {payload_with_core['product'].get('id')}")
    print(f"  sku: {payload_with_core['product'].get('sku')}")
    print(f"  name: {payload_with_core['product'].get('name')}")
    print(f"  custom_attributes: {len(payload_with_core['product']['custom_attributes'])} fields")
    
    with httpx.Client(timeout=60.0) as client:
        response = client.put(url, headers=headers, json=payload_with_core)
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code < 400:
        print("\n✓ SUCCESS with core fields! SEO attributes updated.")

print("\n" + "=" * 80)
