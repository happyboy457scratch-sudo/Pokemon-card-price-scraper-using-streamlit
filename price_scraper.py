import requests
from bs4 import BeautifulSoup
import statistics

def get_ebay_market_data(card_name):
    # This URL uses the '_rss' format which is meant for data reading
    query = f"{card_name} pokemon card"
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1&_rss=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        # RSS feeds use XML format
        soup = BeautifulSoup(response.content, 'xml')
        
        # In RSS, prices are usually tucked inside the 'description' or 'title'
        # We look for all text that looks like a price (e.g., $15.50)
        items = soup.find_all('item')
        
        valid_prices = []
        for item in items:
            title = item.title.text if item.title else ""
            # Some RSS feeds put the price in the title: "Charizard - $50.00"
            price_search = [float(s) for s in title.replace('$', '').replace(',', '').split() if s.replace('.', '', 1).isdigit()]
            
            if price_search:
                price_val = price_search[0]
                if 1.0 < price_val < 5000.0:
                    valid_prices.append(price_val)

        if not valid_prices:
            return None, "eBay RSS returned no items."

        # Average the results
        market_avg = statistics.mean(valid_prices[:10])
        return round(market_avg, 2), len(valid_prices)

    except Exception as e:
        return None, f"Error: {str(e)}"
