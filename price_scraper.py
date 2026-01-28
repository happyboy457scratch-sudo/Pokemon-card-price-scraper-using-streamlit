import requests

def get_card_data(card_name):
    """
    Fetches market price and image URL from the TCGdex API.
    This replaces the old eBay scraper to avoid IP blocks.
    """
    try:
        # 1. Search for the card by name to get its unique ID
        # We use 'en' for English cards
        search_url = f"https://api.tcgdex.net/v2/en/cards?name={card_name}"
        search_response = requests.get(search_url, timeout=10)
        search_results = search_response.json()

        if not search_results:
            return None, "Card not found in database."

        # 2. Get the full details for the first/top match
        card_id = search_results[0]['id']
        detail_url = f"https://api.tcgdex.net/v2/en/cards/{card_id}"
        card_data = requests.get(detail_url, timeout=10).json()

        # 3. Extract the Image and Price
        # We try to get the 'High Quality' image
        image_url = f"{card_data.get('image')}/high.webp"
        
        # We look for the TCGplayer market price (Normal, then Holo, then Reverse)
        pricing = card_data.get('pricing', {}).get('tcgplayer', {})
        market_price = (
            pricing.get('normal', {}).get('market') or 
            pricing.get('holofoil', {}).get('market') or
            pricing.get('reverse', {}).get('market')
        )

        # 4. Return the data as a clean dictionary
        result = {
            "name": card_data.get('name'),
            "set": card_data.get('set', {}).get('name'),
            "price": market_price,
            "image": image_url
        }
        
        return result, "Success"

    except Exception as e:
        return None, f"Connection Error: {str(e)}"
