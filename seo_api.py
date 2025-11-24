import httpx
import json
import logging
import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# ---------------------------
# Configuration and constants
# ---------------------------

META_TITLE_MAX_LEN = 60
META_DESCRIPTION_MAX_LEN = 170

# Magento Store Configuration
MAGENTO_BASE_URL = os.getenv("MAGENTO_BASE_URL", "https://store.example.com")
MAGENTO_API_TOKEN = os.getenv("MAGENTO_API_TOKEN")

logger = logging.getLogger("seo_meta_service")
logging.basicConfig(level=logging.INFO)

# OpenAI client (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI client initialized.")
else:
    client = None
    logger.warning(
        "OPENAI_API_KEY is not set. AI calls will be skipped and fallback generator will be used."
    )

# Validate required Magento credentials
if not MAGENTO_API_TOKEN:
    logger.error(
        "MAGENTO_API_TOKEN environment variable is not set. "
        "Magento API calls will fail. Please set this variable before running."
    )

app = FastAPI(
    title="Magento SEO Meta Generator",
    description=(
        "API to generate SEO metadata (Meta Title, Meta Description, Meta Keywords) "
        "for any Magento store using AI (when available) or a local fallback generator."
    ),
    version="1.0.0",
)


# -----------------
# Data Models
# -----------------

class ProductInput(BaseModel):
    """Represents the input required to generate SEO metadata."""
    name: str = Field(..., example="Blue Wireless Headphones Pro")
    short_description: Optional[str] = Field(
        None,
        example="Premium wireless headphones with active noise cancellation"
    )
    description: Optional[str] = Field(
        None,
        example="Features 40-hour battery life, premium sound quality, and comfortable over-ear design."
    )
    country: str = Field(..., example="BR")
    language: str = Field(..., example="pt-BR")


class SeoMetaOutput(BaseModel):
    """Represents the structured SEO metadata returned by the API."""
    meta_title: str
    meta_description: str
    meta_keywords: str


class SkuInput(BaseModel):
    """Input model to generate SEO starting from a SKU in the Magento store."""
    sku: str = Field(..., example="HEADPHONES-BLUE-PRO")
    language: str = Field(
        "pt-BR",
        example="pt-BR",
        description="Language used for SEO texts.",
    )


# -----------------
# Helper Functions
# -----------------

def truncate_text(text: str, max_length: int) -> str:
    """Truncates a string gracefully and adds '...' if needed."""
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def fetch_product_from_magento(sku: str) -> dict:
    """
    Fetches product information from Magento store by SKU.
    """
    url = f"{MAGENTO_BASE_URL}/rest/V1/products/{sku}"

    headers = {
        "Authorization": f"Bearer {MAGENTO_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(timeout=60.0) as client_http:
            response = client_http.get(url, headers=headers)

        if response.status_code == 404:
            raise RuntimeError(f"Product with SKU '{sku}' not found in Magento store.")

        if response.status_code >= 400:
            raise RuntimeError(
                f"Magento returned error {response.status_code}: {response.text}"
            )

        return response.json()

    except Exception as exc:
        raise RuntimeError(f"Error calling Magento API: {exc}") from exc


def map_magento_product_to_input(data: dict, language: str) -> ProductInput:
    """
    Maps a Magento product JSON payload into our internal ProductInput model.
    This assumes a Magento-like structure with 'name' and 'custom_attributes'.
    """
    name = data.get("name") or ""

    short_desc = None
    description = None

    # Magento usually sends custom attributes as a list of {attribute_code, value}
    custom_attributes = data.get("custom_attributes") or []
    for attr in custom_attributes:
        code = attr.get("attribute_code")
        value = attr.get("value")
        if code == "short_description":
            short_desc = value
        elif code == "description":
            description = value

    return ProductInput(
        name=name,
        short_description=short_desc,
        description=description,
        country="BR",
        language=language,
    )


def build_ai_prompt(product: ProductInput) -> str:
    """Builds the prompt sent to the AI model."""
    return f"""
Generate SEO metadata for the following product.

Product data:
- Name: {product.name}
- Short Description: {product.short_description or "(empty)"}
- Description: {product.description or "(empty)"}
- Country: {product.country}
- Language: {product.language}

Rules:
1. Use the language provided in "Language".
2. Meta Title (max {META_TITLE_MAX_LEN} chars): must include a short summary of the product.
3. Meta Description (max {META_DESCRIPTION_MAX_LEN} chars): include
   - The main benefit
   - 1–2 important features
   - A light call to action (e.g., Visit the store).
4. Meta Keywords:
   - Between 5–10 terms separated by commas.
   - No prices or promotional terms.
5. Respond ONLY with pure JSON:

{{
  "meta_title": "...",
  "meta_description": "...",
  "meta_keywords": "..., ..."
}}
""".strip()


def parse_ai_response(raw_content: str) -> SeoMetaOutput:
    """Parses and validates the JSON returned by the AI model."""
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        logger.error("Invalid JSON from AI: %s", raw_content)
        raise RuntimeError("Invalid JSON returned by AI")

    meta_title = truncate_text(data.get("meta_title", "").strip(), META_TITLE_MAX_LEN)
    meta_description = truncate_text(
        data.get("meta_description", "").strip(),
        META_DESCRIPTION_MAX_LEN,
    )
    meta_keywords = data.get("meta_keywords", "").strip()

    if not meta_title or not meta_description or not meta_keywords:
        raise RuntimeError("Missing fields in AI response")

    return SeoMetaOutput(
        meta_title=meta_title,
        meta_description=meta_description,
        meta_keywords=meta_keywords,
    )


# -----------------
# Fallback SEO generator (no external AI)
# -----------------

def generate_seo_fallback(product: ProductInput) -> SeoMetaOutput:
    """
    Generates simple SEO metadata without calling OpenAI.
    Used when API key is missing, quota is exceeded or any AI error happens.
    """
    name = product.name.strip() or "Produto Premium"

    country_label = "Brasil" if product.country.upper() == "BR" else product.country

    # Meta title
    raw_title = f"{name} | Premium Selection"
    meta_title = truncate_text(raw_title, META_TITLE_MAX_LEN)

    # Meta description
    lang = product.language.lower()
    if lang.startswith("pt"):
        raw_description = (
            f"{name} com qualidade premium para suas necessidades. "
            f"Confira a loja oficial no {country_label}."
        )
    elif lang.startswith("es"):
        raw_description = (
            f"{name} con calidad premium para tus necesidades. "
            f"Visita nuestra tienda oficial en {country_label}."
        )
    else:
        raw_description = (
            f"{name} with premium quality for your needs. "
            f"Visit our official store in {country_label}."
        )

    meta_description = truncate_text(raw_description, META_DESCRIPTION_MAX_LEN)

    # Keywords (simple heuristic from product name)
    words = [
        w.strip(" ,.;:()[\"']")
        for w in name.lower().split()
        if len(w) > 3 and w.lower() not in {"gaming", "notebook"}
    ]
    unique_words: List[str] = []
    for w in words:
        if w not in unique_words:
            unique_words.append(w)

    keywords_list = ["premium", name.lower()]
    keywords_list.extend(unique_words[:6])
    meta_keywords = ", ".join(keywords_list)

    return SeoMetaOutput(
        meta_title=meta_title,
        meta_description=meta_description,
        meta_keywords=meta_keywords,
    )


# -----------------
# Main generator (AI + fallback)
# -----------------

def generate_seo_with_ai(product: ProductInput) -> SeoMetaOutput:
    """
    Tries to generate SEO metadata using OpenAI.
    If anything goes wrong (no key, quota exceeded, etc.),
    falls back to the local generator.
    """
    if not client:
        logger.warning("No OpenAI client configured. Using fallback generator.")
        return generate_seo_fallback(product)

    system_message = (
        "You are an SEO assistant specialized in e-commerce product catalog optimization."
    )

    prompt = build_ai_prompt(product)

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.4,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
        )

        raw_content = completion.choices[0].message.content.strip()
        logger.info("AI Response: %s", raw_content)
        return parse_ai_response(raw_content)

    except Exception as exc:
        logger.warning("AI call failed (%s). Using fallback generator instead.", exc)
        return generate_seo_fallback(product)


# -----------------
# Magento update helpers
# -----------------

def build_product_update_payload(raw_product: dict, seo: SeoMetaOutput) -> dict:
    """
    Builds a Magento product update payload based on the original product JSON.
    This is useful if you want to preserve all existing fields when updating.
    
    Currently not used by apply_seo_to_magento_product (which uses minimal payload),
    but kept for reference and potential future use.
    """
    product_payload: dict = {}

    # Copy core product fields if present
    for key in [
        "id",
        "sku",
        "name",
        "attribute_set_id",
        "price",
        "status",
        "visibility",
        "type_id",
        "weight",
        "extension_attributes",
        "product_links",
        "options",
        "media_gallery_entries",
        "tier_prices",
    ]:
        if key in raw_product:
            product_payload[key] = raw_product[key]

    # Attributes to exclude from the update payload (these cause validation errors)
    excluded_attributes = {
        "tier_price_for_store",  # Causes "double" type error when it's an array
        "category_ids",  # Should use extension_attributes instead
    }

    # Update custom_attributes, preserving everything except SEO fields
    original_custom_attrs = raw_product.get("custom_attributes", [])
    updated_custom_attrs = []
    seen_seo_codes = set()

    for attr in original_custom_attrs:
        code = attr.get("attribute_code")
        value = attr.get("value")
        
        # Skip excluded attributes
        if code in excluded_attributes:
            continue
            
        if code == "meta_title":
            updated_custom_attrs.append(
                {"attribute_code": "meta_title", "value": seo.meta_title}
            )
            seen_seo_codes.add("meta_title")
        elif code == "meta_description":
            updated_custom_attrs.append(
                {"attribute_code": "meta_description", "value": seo.meta_description}
            )
            seen_seo_codes.add("meta_description")
        elif code == "meta_keyword":
            updated_custom_attrs.append(
                {"attribute_code": "meta_keyword", "value": seo.meta_keywords}
            )
            seen_seo_codes.add("meta_keyword")
        else:
            # Keep any other custom attribute as-is
            updated_custom_attrs.append({"attribute_code": code, "value": value})

    # If some SEO attribute did not exist before, we add it
    if "meta_title" not in seen_seo_codes:
        updated_custom_attrs.append(
            {"attribute_code": "meta_title", "value": seo.meta_title}
        )
    if "meta_description" not in seen_seo_codes:
        updated_custom_attrs.append(
            {"attribute_code": "meta_description", "value": seo.meta_description}
        )
    if "meta_keyword" not in seen_seo_codes:
        updated_custom_attrs.append(
            {"attribute_code": "meta_keyword", "value": seo.meta_keywords}
        )

    product_payload["custom_attributes"] = updated_custom_attrs

    return {"product": product_payload}


def apply_seo_to_magento_product(sku: str, seo: SeoMetaOutput) -> dict:
    """
    Updates only SEO meta fields (meta_title, meta_description, meta_keyword)
    for a given product in the Magento store.

    Sends a minimal payload with only the SEO attributes to avoid validation errors.
    """
    url = f"{MAGENTO_BASE_URL}/rest/V1/products/{sku}"

    headers = {
        "Authorization": f"Bearer {MAGENTO_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    timeout = httpx.Timeout(60.0, read=60.0, connect=30.0)

    try:
        # Fetch current product to check if SEO attributes exist
        with httpx.Client(timeout=timeout) as client_http:
            get_response = client_http.get(url, headers=headers)

        if get_response.status_code >= 400:
            logger.error("Failed to fetch product: %s", get_response.text)
            return {
                "ok": False,
                "status_code": get_response.status_code,
                "response_text": f"Failed to fetch product: {get_response.text}",
            }

        current_product = get_response.json()
        
        # Find existing SEO attribute codes to handle variations
        existing_attrs = {attr.get("attribute_code"): attr.get("value") 
                         for attr in current_product.get("custom_attributes", [])}
        
        logger.info("Existing SEO attributes: meta_title=%s, meta_description=%s, meta_keyword=%s",
                   "meta_title" in existing_attrs,
                   "meta_description" in existing_attrs,
                   "meta_keyword" in existing_attrs)

        # Build minimal payload with only the three SEO fields
        custom_attrs = [
            {"attribute_code": "meta_title", "value": seo.meta_title},
            {"attribute_code": "meta_description", "value": seo.meta_description},
            {"attribute_code": "meta_keyword", "value": seo.meta_keywords},
        ]

        payload = {
            "product": {
                "custom_attributes": custom_attrs
            }
        }

        logger.info("Sending update payload: %s", json.dumps(payload, ensure_ascii=False))

        # Send the update
        with httpx.Client(timeout=timeout) as client_http:
            response = client_http.put(url, headers=headers, json=payload)

        ok = response.status_code < 400

        if not ok:
            logger.error("Magento update error %s: %s", response.status_code, response.text)
            
            # Try to get more details
            try:
                error_detail = response.json()
                logger.error("Error detail: %s", json.dumps(error_detail, ensure_ascii=False))
            except:
                pass

        return {
            "ok": ok,
            "status_code": response.status_code,
            "response_text": response.text,
        }

    except Exception as exc:
        logger.error("Exception while calling Magento: %s", exc, exc_info=True)
        return {
            "ok": False,
            "status_code": None,
            "response_text": str(exc),
        }


# -----------------
# API Endpoints
# -----------------

@app.post("/seo-meta", response_model=SeoMetaOutput)
async def generate_seo_meta(product: ProductInput) -> SeoMetaOutput:
    """
    API endpoint to generate SEO metadata from product fields.
    """
    try:
        return generate_seo_with_ai(product)
    except Exception as exc:
        logger.exception("Error while generating SEO metadata")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/seo-meta/sku", response_model=SeoMetaOutput)
async def generate_seo_meta_from_sku(sku_input: SkuInput) -> SeoMetaOutput:
    """
    API endpoint to generate SEO metadata from a SKU in the Magento store.
    - Fetches product from Magento
    - Maps it to ProductInput
    - Reuses the SEO generation logic
    """
    try:
        raw_product = fetch_product_from_magento(sku_input.sku)
        product = map_magento_product_to_input(
            raw_product,
            language=sku_input.language,
        )
        return generate_seo_with_ai(product)
    except Exception as exc:
        logger.exception("Error while generating SEO metadata from SKU")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/seo-meta/sku/apply", response_model=SeoMetaOutput)
async def generate_and_apply_seo_meta_from_sku(
    sku_input: SkuInput,
) -> SeoMetaOutput:
    """
    Generates SEO metadata from a SKU in the Magento store and
    applies the result directly to the product.

    HTTP semantics:
      - 200: SEO generated and Magento successfully updated
      - 502: SEO generated, but Magento failed to save the product
      - 500: Internal error in this service
    """
    try:
        # 1) Fetch product from Magento (only to read name/description)
        raw_product = fetch_product_from_magento(sku_input.sku)

        # 2) Map to our internal ProductInput model
        product = map_magento_product_to_input(
            raw_product,
            language=sku_input.language,
        )

        # 3) Generate SEO (AI + fallback)
        seo = generate_seo_with_ai(product)

        # 4) Apply SEO back to Magento using MINIMAL payload (only custom_attributes)
        magento_result = apply_seo_to_magento_product(sku_input.sku, seo)

        if not magento_result["ok"]:
            # Magento refused to save the product (validation, custom rules, etc.)
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "Magento failed to save product.",
                    "magento_status": magento_result["status_code"],
                    "magento_message": magento_result["response_text"],
                },
            )

        # 5) Success: return the SEO that was applied
        return seo

    except HTTPException:
        # Already a clean HTTP error
        raise
    except Exception as exc:
        logger.exception("Unexpected error while generating or applying SEO metadata")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/test-product/{sku}")
async def test_product_lookup(sku: str):
    """
    Debug endpoint to test product fetch from Magento store.
    Returns the raw Magento JSON.
    """
    try:
        data = fetch_product_from_magento(sku)
        return data
    except Exception as exc:
        logger.exception("Error while fetching product from Magento store")
        raise HTTPException(status_code=500, detail=str(exc))
