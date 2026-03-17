from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from urllib.parse import quote
import sys
sys.stdout.reconfigure(encoding='utf-8')


def search_product_nabiji(query):
    encoded_query = quote(query)
    url = f"https://2nabiji.ge/ge/search?searchText={encoded_query}"
    print(f"🔗 Navigating to: {url}")

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                print(f"❌ Failed to launch browser: {e}")
                return []

            try:
                page = browser.new_page()
                page.goto(url, timeout=10000)
                page.wait_for_timeout(3000)
            except PlaywrightTimeout:
                print("❌ Page took too long to load. Check your internet connection.")
                browser.close()
                return []
            except Exception as e:
                print(f"❌ Failed to load page: {e}")
                browser.close()
                return []

            # pop-up ების bypass-ი
            try:
                close_btn = page.query_selector("button[class*='Button_additional']")
                if close_btn:
                    close_btn.click()
                    print("✅ Popup დაიხურა")
                    page.wait_for_timeout(1000)
            except:
                pass

            cards = page.query_selector_all("[class*='ProductCard_product__']")
            if not cards:
                cards = page.query_selector_all("[class*='ProductCard']")

            if not cards:
                print("⚠️  No product cards found.")
                browser.close()
                return []

            results = []
            for card in cards:
                try:
                    # Name
                    name_el = card.query_selector("a[class*='ProductCard_title']")
                    name = name_el.inner_text().strip() if name_el else "Unknown"

                    # Current price
                    price_el = card.query_selector("a[class*='ProductCard_productInfo__price__']")
                    price = price_el.query_selector("span").inner_text().strip() if price_el else "N/A"

                    # Old price (before discount)
                    old_price_el = card.query_selector("a[class*='ProductCard_productInfo__price_discount']")
                    old_price = old_price_el.query_selector("span").inner_text().strip() if old_price_el else None

                    link_el = card.query_selector("a[class*='ProductCard_title']")
                    link = "https://2nabiji.ge" + link_el.get_attribute("href") if link_el else ""

                    # skip empty/duplicate entries
                    if name == "Unknown" and price == "N/A":
                        continue

                    results.append({
                        "name": name,
                        "price now": price,
                        "old price": old_price,
                        "url": link,
                    })
                except Exception as e:
                    print(f"⚠️  Skipped a card due to error: {e}")
                    continue

            browser.close()
            print(results)
            return results

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []


def filtered_results_nabiji(results, query):

    filtered = []
    for p in results:
        if p['name'] != "Unknown" and p['price now'] != "N/A" and query.lower() in p['name'].lower():
            filtered.append(p)
    print(filtered)
    store_name_nabiji = "2nabiji"
    return filtered,store_name_nabiji