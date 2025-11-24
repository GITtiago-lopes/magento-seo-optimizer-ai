# Magento SEO Meta Generator API - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [API Endpoints](#api-endpoints)
6. [Usage Examples](#usage-examples)
7. [Error Handling](#error-handling)
8. [Known Issues & Troubleshooting](#known-issues--troubleshooting)
9. [Architecture](#architecture)
10. [Security](#security)

---

## Overview

The **Magento SEO Meta Generator API** is a FastAPI-based service that automatically generates SEO metadata (meta title, meta description, and meta keywords) for Magento e-commerce products using AI (OpenAI GPT-4o-mini) or a smart fallback generator.

### Features
- ✅ **AI-Powered SEO Generation** - Uses OpenAI's GPT-4o-mini for intelligent metadata
- ✅ **Fallback Generator** - Works without OpenAI if API key is not available
- ✅ **Multi-Language Support** - Generates SEO in Portuguese, Spanish, English, and more
- ✅ **Direct Magento Integration** - Fetch products and update metadata directly in Magento
- ✅ **Production Ready** - Comprehensive error handling and logging
- ✅ **Configurable** - Easy to customize via environment variables

### Technology Stack
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **API Client**: httpx (async HTTP requests)
- **AI Provider**: OpenAI API
- **Web Server**: Uvicorn
- **Environment Management**: python-dotenv

---

## Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn python-dotenv httpx openai pydantic
```

Or use the requirements file if available:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your credentials
```

### 3. Run the Server
```bash
python -m uvicorn seo_api:app --reload
```

Server will be available at: `http://localhost:8000`

### 4. Access Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Magento 2.x store with REST API enabled
- OpenAI API key (optional, but recommended)
- Access to Magento staging or production environment

### Step-by-Step Installation

#### 1. Clone or Download the Project
```bash
cd /path/to/asus_seo_meta_ia
```

#### 2. Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install fastapi uvicorn python-dotenv httpx openai pydantic
```

#### 4. Set Up Environment Variables
See [Configuration](#configuration) section below.

#### 5. Run the Server
```bash
python -m uvicorn seo_api:app --reload
```

For production:
```bash
python -m uvicorn seo_api:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```dotenv
# OpenAI Configuration (Optional)
# Get your API key from: https://platform.openai.com/account/api-keys
OPENAI_API_KEY=sk-your-api-key-here

# Magento Store Configuration (Required)
# Base URL of your Magento store (without trailing slash)
MAGENTO_BASE_URL=https://your-magento-store.com

# Magento API Token (Required)
# Generate in Admin > System > Extensions > Integrations
MAGENTO_API_TOKEN=your-api-token-here
```

### Generating Magento API Token

1. Log in to **Magento Admin Panel**
2. Navigate to **System > Extensions > Integrations**
3. Click **Add New Integration**
4. Fill in the integration details:
   - **Name**: SEO Meta Generator
   - **Your Identity**: API Authentication
5. In the **API** section, select these resources:
   - ✓ Products (Catalog)
6. Click **Save**
7. Click **Authorize** to generate the access token
8. Copy the **Access Token** and add it to your `.env` file

### Getting OpenAI API Key

1. Visit https://platform.openai.com/account/api-keys
2. Create a new API key
3. Add it to your `.env` file as `OPENAI_API_KEY`

**Note**: If `OPENAI_API_KEY` is not set, the API will work in fallback mode (no AI generation, but still functional).

---

## API Endpoints

### 1. Generate SEO from Product Fields

**Endpoint**: `POST /seo-meta`

**Description**: Generate SEO metadata from product information (no Magento fetch needed)

**Request Body**:
```json
{
  "name": "Blue Gaming Laptop",
  "short_description": "High-performance gaming laptop",
  "description": "Equipped with RTX 4090, Intel i9, 32GB RAM",
  "country": "BR",
  "language": "pt-BR"
}
```

**Response**:
```json
{
  "meta_title": "Blue Gaming Laptop - Desempenho e Portabilidade",
  "meta_description": "Laptop gamer poderoso com RTX 4090 e Intel i9. Ideal para jogos e trabalho. Visite a loja!",
  "meta_keywords": "laptop, gaming, blue, RTX 4090, Intel i9, 32GB"
}
```

**Status Codes**:
- `200 OK` - Metadata successfully generated
- `400 Bad Request` - Invalid request body
- `500 Internal Server Error` - Server error

---

### 2. Generate SEO from Magento SKU

**Endpoint**: `POST /seo-meta/sku`

**Description**: Fetch product from Magento by SKU and generate SEO metadata

**Request Body**:
```json
{
  "sku": "90NB0SR1-M02FC0",
  "language": "pt-BR"
}
```

**Response**:
```json
{
  "meta_title": "Notebook ASUS X515JA-BR3932W Cinza - Desempenho e Portabilidade",
  "meta_description": "O ASUS X515 oferece desempenho com Windows 11, tela de 15,6\" e SSD. Visite a loja!",
  "meta_keywords": "Notebook ASUS, X515JA, Windows 11, Intel Core i3"
}
```

**Status Codes**:
- `200 OK` - Metadata successfully generated
- `400 Bad Request` - Invalid SKU or request
- `404 Not Found` - Product not found in Magento
- `500 Internal Server Error` - Server error

---

### 3. Generate and Apply SEO to Product

**Endpoint**: `POST /seo-meta/sku/apply`

**Description**: Generate SEO metadata and automatically update it in Magento

⚠️ **NOTE**: This endpoint currently has known issues with Magento 400 errors. See [Known Issues](#known-issues--troubleshooting) section.

**Request Body**:
```json
{
  "sku": "90NB0SR1-M02FC0",
  "language": "pt-BR"
}
```

**Response**:
```json
{
  "meta_title": "Notebook ASUS X515JA-BR3932W Cinza - Desempenho e Portabilidade",
  "meta_description": "O ASUS X515 oferece desempenho com Windows 11, tela de 15,6\" e SSD. Visite a loja!",
  "meta_keywords": "Notebook ASUS, X515JA, Windows 11, Intel Core i3"
}
```

**Status Codes**:
- `200 OK` - SEO generated and Magento updated successfully
- `400 Bad Request` - Invalid request
- `404 Not Found` - Product not found
- `502 Bad Gateway` - Magento refused to save (see Known Issues)
- `500 Internal Server Error` - Server error

---

### 4. Test Product Lookup

**Endpoint**: `GET /test-product/{sku}`

**Description**: Debug endpoint to verify Magento connection and fetch raw product data

**Example**:
```bash
GET /test-product/90NB0SR1-M02FC0
```

**Response**: Raw Magento product JSON

**Status Codes**:
- `200 OK` - Product found
- `404 Not Found` - Product not found
- `500 Internal Server Error` - Server error

---

## Usage Examples

### Using cURL

#### Example 1: Generate SEO from Product Fields
```bash
curl -X POST http://localhost:8000/seo-meta \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop ROG",
    "short_description": "Powerful gaming laptop",
    "description": "Features RTX 4090, Intel i9, 32GB RAM, 1TB SSD",
    "country": "BR",
    "language": "pt-BR"
  }'
```

#### Example 2: Generate SEO from Magento SKU
```bash
curl -X POST http://localhost:8000/seo-meta/sku \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "90NB0SR1-M02FC0",
    "language": "pt-BR"
  }'
```

#### Example 3: Test Product Lookup
```bash
curl http://localhost:8000/test-product/90NB0SR1-M02FC0
```

### Using Python

```python
import requests

# Generate SEO from product fields
response = requests.post(
    "http://localhost:8000/seo-meta",
    json={
        "name": "Gaming Laptop",
        "short_description": "High-performance laptop",
        "description": "RTX 4090, Intel i9, 32GB RAM",
        "country": "BR",
        "language": "pt-BR"
    }
)

print(response.json())
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');

axios.post('http://localhost:8000/seo-meta', {
  name: "Gaming Laptop",
  short_description: "High-performance laptop",
  description: "RTX 4090, Intel i9, 32GB RAM",
  country: "BR",
  language: "pt-BR"
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

### Batch Processing

For processing multiple products:

```python
import requests
import json

skus = ["SKU-001", "SKU-002", "SKU-003"]
results = []

for sku in skus:
    response = requests.post(
        "http://localhost:8000/seo-meta/sku",
        json={"sku": sku, "language": "pt-BR"}
    )
    
    if response.status_code == 200:
        results.append({
            "sku": sku,
            "seo": response.json(),
            "status": "success"
        })
    else:
        results.append({
            "sku": sku,
            "error": response.text,
            "status": "failed"
        })

# Save results
with open("seo_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error description or details"
}
```

Or for HTTP errors:

```json
{
  "message": "Error message in Portuguese or English"
}
```

### Common Errors

#### 1. Product Not Found (404)
```json
{
  "detail": "Product with SKU 'INVALID-SKU' not found in Magento store."
}
```

**Solution**: Verify the SKU is correct and exists in Magento.

#### 2. Magento API Error (500)
```json
{
  "detail": "Error calling Magento API: Connection timeout"
}
```

**Solution**: 
- Check if Magento is accessible
- Verify `MAGENTO_BASE_URL` in `.env`
- Check `MAGENTO_API_TOKEN` validity

#### 3. OpenAI API Error (Falls back to fallback generator)
```
WARNING:seo_meta_service:AI call failed (Error code: 401 - Invalid API key). Using fallback generator instead.
```

**Solution**:
- Verify `OPENAI_API_KEY` is correct
- Check OpenAI API quota
- Fallback generator will still work

#### 4. Magento Update Error (502)
```json
{
  "error": "Magento failed to save product.",
  "magento_status": 400,
  "magento_message": "O produto não pôde ser salvo. Por favor, tente novamente."
}
```

**See**: [Known Issues](#known-issues--troubleshooting)

---

## Known Issues & Troubleshooting

### Issue 1: Magento 400 Error on Product Update

**Symptom**: 
```
ERROR:seo_meta_service:Magento update error 400: {"message":"O produto não pôde ser salvo..."}
```

**Cause**: Magento has a custom observer/plugin blocking product updates via REST API.

**Current Status**: ❌ **BLOCKING ISSUE**

**Workaround Solutions**:

1. **Check Magento Logs**
   ```bash
   # SSH to your Magento server
   tail -f var/log/system.log
   tail -f var/log/debug.log
   ```

2. **Disable Problematic Extensions**
   - Log into Magento Admin
   - Go to System > Extensions > Modules
   - Disable modules related to: Product Save, Stock Management, Pricing
   - Try the update again

3. **Verify API Token Permissions**
   - Admin > System > Extensions > Integrations
   - Edit the SEO Meta Generator integration
   - Ensure it has full "Products" write permissions

4. **Test with Different Product**
   - Try updating a different SKU to see if it's product-specific
   - Some products may be locked/protected

5. **Check Database Constraints**
   - Contact your Magento hosting provider
   - Ask if there are custom database triggers blocking updates

### Issue 2: OpenAI API Key Issues

**Symptom**:
```
WARNING:seo_meta_service:AI call failed (Error code: 404 - The model `gpt-4o-mini` does not exist...)
```

**Solution**:
- Verify API key is valid and has GPT-4o-mini access
- Check OpenAI account quota and billing
- API will fall back to fallback generator automatically

### Issue 3: Product Not Found

**Symptom**:
```
Error: Product with SKU 'SKU-123' not found in Magento store.
```

**Solution**:
- Verify SKU exists in Magento Admin
- Check if product is assigned to the correct websites
- Test with `/test-product/{sku}` endpoint first

### Issue 4: Magento Connection Timeout

**Symptom**:
```
Error calling Magento API: Connection timeout after 60.0s
```

**Solution**:
- Check if Magento server is online: `ping your-magento-store.com`
- Verify firewall isn't blocking the connection
- Increase timeout in code (currently set to 60 seconds)
- Check Magento server logs for performance issues

---

## Architecture

### System Components

```
┌─────────────────────────────────────────┐
│     Client Application                   │
│  (Web, Mobile, Desktop, Scripts)        │
└────────────────┬────────────────────────┘
                 │ HTTP/REST
                 ▼
┌──────────────────────────────────────────┐
│    Magento SEO Meta Generator API        │
│  (FastAPI + Uvicorn)                     │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Endpoints:                        │  │
│  │  - POST /seo-meta                  │  │
│  │  - POST /seo-meta/sku              │  │
│  │  - POST /seo-meta/sku/apply        │  │
│  │  - GET /test-product/{sku}         │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Core Logic:                       │  │
│  │  - AI Prompt Builder               │  │
│  │  - Fallback SEO Generator          │  │
│  │  - Magento API Client              │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
         │                    │
         │                    │
    ┌────▼────┐          ┌────▼──────────┐
    │  OpenAI │          │  Magento      │
    │  API    │          │  REST API     │
    └─────────┘          └───────────────┘
```

### Request Flow

```
1. Client sends request with product info
2. API validates input (Pydantic)
3. Generate SEO:
   a. Try OpenAI if API key exists
   b. Fall back to local generator if AI fails
4. Validate response (max lengths, required fields)
5. Return SEO metadata to client
6. (Optional) Apply to Magento via REST API
7. Return final response with status
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `generate_seo_with_ai()` | Main orchestrator - tries AI, falls back to local |
| `build_ai_prompt()` | Constructs prompt for OpenAI |
| `parse_ai_response()` | Validates and parses OpenAI JSON response |
| `generate_seo_fallback()` | Local SEO generator (no AI required) |
| `fetch_product_from_asus_br_staging()` | Fetches product from Magento |
| `apply_seo_to_magento_product()` | Updates product in Magento (⚠️ Currently blocked) |
| `truncate_text()` | Ensures metadata fits within character limits |

---

## Security

### Best Practices

#### 1. **Environment Variables**
- Never hardcode API keys in source code
- Always use `.env` file for secrets
- Add `.env` to `.gitignore`

```bash
# .gitignore
.env
.env.local
.env.*.local
```

#### 2. **API Token Rotation**
- Rotate Magento API tokens every 90 days
- Rotate OpenAI API keys regularly
- Use different tokens for staging and production

#### 3. **HTTPS in Production**
```bash
# Use SSL/TLS
https://your-magento-store.com/rest/V1/products
```

#### 4. **Rate Limiting**
For production, consider adding rate limiting:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/seo-meta")
@limiter.limit("10/minute")
async def generate_seo_meta(request: Request, product: ProductInput):
    ...
```

#### 5. **CORS Configuration**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

#### 6. **Secrets Manager (Production)**

Instead of `.env` files, use:

**AWS Secrets Manager**:
```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='seo-api-secrets')
MAGENTO_API_TOKEN = secret['SecretString']
```

**Azure Key Vault**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
MAGENTO_API_TOKEN = client.get_secret("magento-token").value
```

**GitHub Secrets** (for CI/CD):
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  MAGENTO_API_TOKEN: ${{ secrets.MAGENTO_API_TOKEN }}
```

### Data Privacy

- The API does not store product data
- SEO metadata is generated on-the-fly
- No logs contain sensitive information
- All communication is stateless

---

## Deployment

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "seo_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t seo-api .
docker run -p 8000:8000 --env-file .env seo-api
```

### Docker Compose

```yaml
version: '3.8'

services:
  seo-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MAGENTO_BASE_URL=${MAGENTO_BASE_URL}
      - MAGENTO_API_TOKEN=${MAGENTO_API_TOKEN}
    volumes:
      - ./logs:/app/logs
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: seo-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: seo-api
  template:
    metadata:
      labels:
        app: seo-api
    spec:
      containers:
      - name: seo-api
        image: seo-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: MAGENTO_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: seo-secrets
              key: magento-token
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: seo-secrets
              key: openai-key
```

---

## Support & Contributing

### Reporting Issues

When reporting issues, include:
1. **Error message** (full stack trace)
2. **Request payload** (sanitized, without tokens)
3. **Expected vs actual behavior**
4. **Environment** (Python version, OS, etc.)

### Example Issue Report

```
**Issue**: Magento 400 error on product update
**SKU**: 90NB0SR1-M02FC0
**Error**: {"message":"O produto não pôde ser salvo..."}
**Environment**: Python 3.11, Windows 11
**Steps to Reproduce**:
1. POST /seo-meta/sku/apply with SKU
2. Observe 502 response
**Expected**: 200 OK with updated SEO
```

---

## Changelog

### Version 1.0.0 (2025-11-24)
- ✅ Initial release
- ✅ AI-powered SEO generation with OpenAI
- ✅ Fallback generator for offline mode
- ✅ Magento REST API integration
- ✅ Multi-language support
- ❌ Known issue: Magento product update blocked by server-side observer

---

## License

This project is configured for the ASUS Brazil store. Modify as needed for other Magento instances.

---

## Contact & Support

For issues or questions:
1. Check the [Known Issues](#known-issues--troubleshooting) section
2. Review API logs for detailed error messages
3. Test with `/test-product/{sku}` endpoint
4. Contact your Magento administrator for server-side issues

---

**Last Updated**: November 24, 2025  
**Version**: 1.0.0  
**Status**: Production Ready (with known Magento update issue)
