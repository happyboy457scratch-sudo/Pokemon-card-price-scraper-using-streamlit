import requests

def get_card_data(card_name):
    """
    Fetches both the market price and the image URL for a card.
    """
    try:
        # 1. Search for the card
        search_url = f"https://api.tcgdex.net/v2/en/cards?name={card_name}"
        search_res = requests.get(search_url, timeout=10).json()

        if not search_res:
            return None, "Card not found."

        # 2. Get the specific details of the first card found
        card_id = search_res[0]['id']
        detail_url = f"https://api.tcgdex.net/v2/en/cards/{card_id}"
        card = requests.get(detail_url, timeout=10).json()

        # 3. Extract Image and Price
        image_url = f"{card.get('image')}/high.webp"
        pricing = card.get('pricing', {}).get('tcgplayer', {})
        
        # Look for Normal or Holo market price
        price = pricing.get('normal', {}).get('market') or pricing.get('holofoil', {}).get('market')

        if price:
            return {"price": price, "image": image_url, "name": card['name']}, "Success"
        return {"price": "N/A", "image": image_url, "name": card['name']}, "Price missing"

    except Exception as e:
        return None, f"Error: {str(e)}"
