import requests
from bs4 import BeautifulSoup
import statistics

def get_ebay_market_data(card_name):
    # Adding "pokemon card" to the search helps eBay's algorithm
    query = f"{card_name} pokemon card"
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
    
    # A more robust "User-Agent" to look like a modern browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # If eBay blocks us, we'll see a 403 or 503 error
        if response.status_code != 200:
            return None, f"eBay blocked the request (Error {response.status_code})"

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # eBay often changes its CSS classes. We try multiple known price classes.
        price_tags = soup.select('.s-item__price') 
        
        valid_prices = []
        for tag in price_tags:
            text = tag.get_text().replace('$', '').replace(',', '').strip()
            # Handle price ranges like "10.00 to 12.00"
            if 'to' in text:
                text = text.split('to')[0].strip()
            
            try:
                price_val = float(text)
                # Filter out outliers (like $0.99 items or extreme high ends)
                if 1.0 < price_val < 10000.0:
                    valid_prices.append(price_val)
            except ValueError:
                continue

        # eBay search results often include a "hidden" first item that is an ad
        # We skip the first one if the list is long enough
        if len(valid_prices) > 1:
            valid_prices = valid_prices[1:]

        if not valid_prices:
            return None, "No recent sold listings found."

        # Average the most recent 10 sales
        final_list = valid_prices[:10]
        market_avg = statistics.mean(final_list)
        
        return round(market_avg, 2), len(valid_prices)

    except Exception as e:
        return None, f"Connection failed: {str(e)}"
