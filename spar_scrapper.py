import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

SPAR_BASE_URL = "https://sparonline.ge"
SPAR_API_URL  = "https://api.spargeorgia.com/v1/Products/v3"
STORE_NAME    = "Spar"
SHOP_ID       = 21


def _get_fresh_token() -> str:
    try:
        resp = requests.get(
            SPAR_BASE_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        match = re.search(r'"accessToken"\s*:\s*"([^"]+)"', resp.text)
        if match:
            print("✅ Fresh Spar token fetched")
            return match.group(1)
    except Exception as e:
        print(f"⚠️  Token fetch failed: {e}")
    return ""


def search_product_spar(query: str) -> list[dict]:
    print(f"🔗 Calling Spar API for: {query}")

    token = _get_fresh_token()
    if not token:
        print("❌ Could not obtain token — aborting Spar scrape")
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
        "Origin":        SPAR_BASE_URL,
        "Referer":       SPAR_BASE_URL,
        "User-Agent":    "Mozilla/5.0",
    }

    params = {
        "ShopId":    SHOP_ID,
        "Name":      query,
        "PageIndex": 0,
        "PageSize":  50,
    }

    try:
        resp = requests.get(
            SPAR_API_URL,
            headers=headers,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        print("❌ Spar API timed out.")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ Spar API HTTP error: {e} — {resp.text[:300]}")
        return []
    except Exception as e:
        print(f"❌ Spar API error: {e}")
        return []

    items = (
        data
        if isinstance(data, list)
        else data.get("items")
        or data.get("products")
        or data.get("data")
        or data.get("results")
        or []
    )

    if not items:
        print(f"⚠️  Empty response. Keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
        return []

    print(f"🔍 First item keys: {list(items[0].keys())}")

    results = []
    for item in items:
        try:
            name = (
                item.get("name")
                or item.get("title")
                or item.get("productName")
                or "Unknown"
            )
            price_now = (
                item.get("salePrice")
                or item.get("discountedPrice")
                or item.get("currentPrice")
                or item.get("price")
                or "N/A"
            )
            old_price = (
                item.get("originalPrice")
                or item.get("regularPrice")
                or item.get("oldPrice")
                or item.get("compareAtPrice")
                or None
            )

            price_now = str(price_now) if price_now != "N/A" else "N/A"
            old_price = str(old_price) if old_price else None

            slug = item.get("slug") or item.get("url") or item.get("id") or ""
            url  = f"{SPAR_BASE_URL}/product/{slug}" if slug else ""

            if name == "Unknown" and price_now == "N/A":
                continue

            results.append({
                "name":      name,
                "price now": price_now,
                "old price": old_price,
                "url":       url,
            })
        except Exception as e:
            print(f"⚠️  Skipped item: {e}")
            continue

    print(f"✅ Spar: {len(results)} products found")
    return results


def filtered_results_spar(results: list[dict], query: str) -> tuple[list[dict], str]:
    filtered = [
        p for p in results
        if p["name"] != "Unknown"
        and p["price now"] != "N/A"
    ]
    print(f"✅ Spar filtered: {len(filtered)} results for '{query}'")
    return filtered, STORE_NAME