import requests
from bs4 import BeautifulSoup
import statistics
import re

def get_ebay_market_data(card_name):
    """
    Scrapes eBay sold listings and returns a cleaned market average.
    """
    # 1. Target SOLD and COMPLETED listings specifically
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={card_name.replace(' ', '+')}+pokemon+card&LH_Sold=1&LH_Complete=1"
    
    # 2. Browser Disguise (Headers) to prevent getting blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, "Connection Error"

        soup = BeautifulSoup(response.text, 'html.parser')
        # eBay's price class for search results
        price_elements = soup.find_all('span', {'class': 's-item__price'})
        
        valid_prices = []
        for item in price_elements:
            # Remove $, commas, and handle "to" ranges
            raw_text = item.get_text().replace('$', '').replace(',', '')
            if 'to' in raw_text:
                raw_text = raw_text.split('to')[0]
            
            try:
                price_val = float(raw_text.strip())
                # Filter out 'noise' like $0.99 shipping-only listings
                if price_val > 1.0:
                    valid_prices.append(price_val)
            except ValueError:
                continue

        if not valid_prices:
            return None, "No Sales Found"

        # 3. PriceCharting Logic: Trim the outliers
        # We remove the highest and lowest 10% to get a 'true' middle price
        valid_prices.sort()
        if len(valid_prices) > 5:
            trim_count = max(1, len(valid_prices) // 10)
            cleaned_list = valid_prices[trim_count:-trim_count]
        else:
            cleaned_list = valid_prices

        market_avg = statistics.mean(cleaned_list)
        return round(market_avg, 2), len(valid_prices)

    except Exception as e:
        return None, str(e)
