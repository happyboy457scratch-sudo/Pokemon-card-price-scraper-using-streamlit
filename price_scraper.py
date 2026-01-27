import requests
from bs4 import BeautifulSoup
import json
import sys
import re

def get_ebay_average(card_name):
    # This URL filters for "Sold" and "Completed" listings
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={card_name.replace(' ', '+')}+pokemon+card&LH_Sold=1&LH_Complete=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all price elements on the page
        price_elements = soup.find_all('span', {'class': 's-item__price'})
        
        prices = []
        for item in price_elements:
            # Clean the text: remove $, commas, and handle price ranges (e.g., "$10 to $12")
            raw_price = item.text.replace('$', '').replace(',', '')
            if 'to' in raw_price:
                raw_price = raw_price.split('to')[0] # Take the lower end of a range
            
            try:
                prices.append(float(raw_price))
            except ValueError:
                continue

        # Use the first 5 "Sold" listings to get a recent average
        recent_prices = prices[:5] 
        
        if not recent_prices:
            return "No Sales Found"
            
        avg = sum(recent_prices) / len(recent_prices)
        return f"${avg:.2f}"

    except Exception as e:
        return f"Error: {str(e)}"

# Get input from GitHub Action
card_query = sys.argv[1] if len(sys.argv) > 1 else "Pikachu"

print(f"🕵️‍♂️ Checking recent eBay sales for: {card_query}")
average_price = get_ebay_average(card_query)

# Save the result
output = {card_query: average_price}
with open("prices.json", "w") as f:
    json.dump(output, f, indent=4)

print(f"✅ Market Average: {average_price}")
