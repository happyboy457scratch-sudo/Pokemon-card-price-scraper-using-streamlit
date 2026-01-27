import requests
import json
import sys

# 1. Safely get the card name from GitHub
try:
    # This catches the name you typed in the box
    card_query = sys.argv[1] if len(sys.argv) > 1 else "Pikachu"
except Exception as e:
    card_query = "Pikachu"

def get_price(query):
    try:
        # Search for the card to get the ID
        search_url = f"https://api.tcgdex.net/v2/en/cards?name={query}"
        search_res = requests.get(search_url, timeout=10)
        search_data = search_res.json()
        
        if not search_data:
            return "Card not found"
        
        # Get the first match
        card_id = search_data[0]['id']
        
        # Get the full details for that card
        detail_url = f"https://api.tcgdex.net/v2/en/cards/{card_id}"
        detail_res = requests.get(detail_url, timeout=10)
        data = detail_res.json()
        
        # Dig for the price in the TCGplayer section
        pricing = data.get("pricing", {}).get("tcgplayer", {})
        # Check different versions (normal or holofoil)
        price = pricing.get("normal", {}).get("market") or pricing.get("holofoil", {}).get("market")
        
        return f"${price}" if price else "Price data missing"
    except Exception as e:
        return f"Error: {str(e)}"

# 2. Run the check
print(f"🔍 Searching for: {card_query}")
result_price = get_price(card_query)

# 3. Save it to the JSON file
output = {card_query: result_price}
with open("prices.json", "w") as f:
    json.dump(output, f, indent=4)

print(f"✅ Result: {card_query} is {result_price}")
