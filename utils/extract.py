import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}


def fetching_content(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_fashion_data(product_div):
    product_details = product_div.find('div', class_='product-details')
    if not product_details:
        return {}

    # Title
    title_tag = product_details.find('h3', class_='product-title')
    title = title_tag.text.strip() if title_tag else None

    # Price
    price_container = product_details.find('div', class_='price-container')
    price = None
    if price_container:
        price_span = price_container.find('span', class_='price')
        if price_span:
            price = price_span.text.strip()

    # Other attributes
    rating = colors = size = gender = None
    for p in product_details.find_all('p'):
        text = p.text.strip()
        lower = text.lower()
        if "rating" in lower:
            rating = text.split(':', 1)[-1].strip()
        elif "color" in lower:
            colors = text
        elif "size" in lower:
            size = text.split(':', 1)[-1].strip().upper()
        elif "gender" in lower:
            gender = text.split(':', 1)[-1].strip().lower()

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "colors": colors,
        "size": size,
        "gender": gender,
        "timestamp": datetime.now().isoformat()
    }


def scrape_all_pages(base_url, delay=1):
    all_data = []
    page = 1

    while True:
        current_url = base_url if page == 1 else f"{base_url.rstrip('/')}/page{page}"
        print(f"Scraping page {page}: {current_url}")

        html = fetching_content(current_url)
        if html is None:
            print("Failed to fetch content. Stopping.")
            break

        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('div', class_='collection-card')
        if not cards:
            print("No more products found. Done.")
            break

        for card in cards:
            all_data.append(extract_fashion_data(card))

        if soup.find('li', class_='next'):
            page += 1
            time.sleep(delay)
        else:
            print("No more pages.")
            break

    return all_data


def extract_all_products_from_url(url):
    html = fetching_content(url)
    if html is None:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    return [extract_fashion_data(card) for card in soup.find_all('div', class_='collection-card')]
