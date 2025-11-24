# Magento SEO Meta Generator - Setup Guide

## Environment Configuration

This API requires environment variables for your Magento store credentials. Follow these steps to set up:

### 1. Create `.env` file

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Fill in your credentials

Edit `.env` and add your actual values:

```
OPENAI_API_KEY=sk-your-actual-api-key
MAGENTO_BASE_URL=https://your-magento-store.com
MAGENTO_API_TOKEN=your-actual-magento-token
```

### 3. (Optional) Install python-dotenv for local development

If you want automatic `.env` loading:
```bash
pip install python-dotenv
```

Then add this to the top of `seo_api.py`:
```python
from dotenv import load_dotenv
load_dotenv()  # Automatically loads .env file
```

### 4. Environment Variables Explained

- **OPENAI_API_KEY**: Your OpenAI API key (optional)
  - If not set, the service will use fallback SEO generation
  - Get one at: https://platform.openai.com/account/api-keys

- **MAGENTO_BASE_URL**: Your Magento store base URL (required)
  - Example: `https://myshop.com` or `https://shop.example.com`
  - Do NOT include trailing slash

- **MAGENTO_API_TOKEN**: Magento API authentication token (required)
  - Generate in: Admin > System > Extensions > Integrations
  - Create a new integration with REST API access to Product resources

### 5. Generating Magento API Token

1. Log in to Magento Admin Panel
2. Go to **System > Extensions > Integrations**
3. Click **Add New Integration**
4. Fill in the integration details:
   - **Name**: SEO Meta Generator
   - **Your Identity**: API Authentication
5. In **API** section, select these resources:
   - Products (Catalog)
6. Click **Save**
7. Copy the generated **Access Token** to your `.env` file

### 6. Security Notes

- **Never commit `.env` to git** - it's in `.gitignore`
- Use `.env.example` as a template for documentation
- Rotate your API tokens regularly
- In production, use a secrets manager:
  - AWS Secrets Manager
  - Azure Key Vault
  - HashiCorp Vault
  - GitHub Secrets (for CI/CD)

### 7. Deployment

**Docker:**
```dockerfile
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV MAGENTO_BASE_URL=${MAGENTO_BASE_URL}
ENV MAGENTO_API_TOKEN=${MAGENTO_API_TOKEN}
```

**Kubernetes:**
```yaml
env:
  - name: MAGENTO_API_TOKEN
    valueFrom:
      secretKeyRef:
        name: magento-secrets
        key: api-token
```

**CI/CD (GitHub Actions):**
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  MAGENTO_BASE_URL: ${{ secrets.MAGENTO_BASE_URL }}
  MAGENTO_API_TOKEN: ${{ secrets.MAGENTO_API_TOKEN }}
```

## API Usage

### Generate SEO metadata from product fields

```bash
curl -X POST "http://localhost:8000/seo-meta" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Blue Gaming Laptop",
    "short_description": "High-performance gaming laptop",
    "description": "Equipped with RTX 4090, Intel i9, 32GB RAM",
    "country": "BR",
    "language": "pt-BR"
  }'
```

### Generate SEO from SKU (fetch from Magento)

```bash
curl -X POST "http://localhost:8000/seo-meta/sku" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PROD-SKU-123",
    "language": "pt-BR"
  }'
```

### Generate and apply SEO to product

```bash
curl -X POST "http://localhost:8000/seo-meta/sku/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PROD-SKU-123",
    "language": "pt-BR"
  }'
```

### Test Magento connection

```bash
curl "http://localhost:8000/test-product/PROD-SKU-123"
```
