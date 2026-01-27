import requests

def get_market_price(card_name):
    try:
        # 1. Search for the card to get its unique ID
        search_url = f"https://api.tcgdex.net/v2/en/cards?name={card_name}"
        search_response = requests.get(search_url, timeout=10)
        cards = search_response.json()

        if not cards:
            return None, "Card not found in database."

        # 2. Get the specific price for the first match
        card_id = cards[0]['id']
        detail_url = f"https://api.tcgdex.net/v2/en/cards/{card_id}"
        detail_response = requests.get(detail_url, timeout=10)
        data = detail_response.json()

        # 3. Dig into the TCGplayer price (Standard 'Market' Price)
        pricing = data.get('pricing', {}).get('tcgplayer', {})
        
        # Check for Normal or Holo prices
        market_price = pricing.get('normal', {}).get('market') or pricing.get('holofoil', {}).get('market')

        if market_price:
            return market_price, "Success"
        return None, "Price data currently unavailable for this card."
        
    except Exception as e:
        return None, f"Error: {str(e)}"
