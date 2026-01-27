import requests
import json

def get_tcgdex_price(card_id):
    # This hits the TCGdex API for the specific card ID
    url = f"https://api.tcgdex.net/v2/en/cards/{card_id}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        # Digging into the pricing object shown in your screenshot
        tcgplayer = data.get("pricing", {}).get("tcgplayer", {})
        
        # We check 'reverse-holofoil' first (where the 0.3 is), then 'normal'
        # Using .get() ensures it doesn't crash if one variant is missing
        rev_holo = tcgplayer.get("reverse-holofoil", {}).get("marketPrice")
        normal = tcgplayer.get("normal", {}).get("marketPrice")
        
        # Pick the first available price
        final_price = rev_holo or normal or "N/A"
        return f"${final_price}" if final_price != "N/A" else "N/A"
    except Exception as e:
        print(f"Error fetching {card_id}: {e}")
        return "N/A"

# --- YOUR TRACKING LIST ---
# Add any cards you want here. The ID is found in the TCGdex URL.
cards_to_track = {
    "Furret (Darkness Ablaze)": "swsh3-136",
    "Pikachu (151)": "sv3pt5-173"
}

# Dictionary to hold the final dump
price_dump = {}

print("⚡ Starting Price Scrape...")
for name, cid in cards_to_track.items():
    price_dump[name] = get_tcgdex_price(cid)
    print(f"Done: {name} -> {price_dump[name]}")

# --- SAVE THE JSON FILE ---
# This is the file your streamlit_app.py will read
with open("prices.json", "w") as f:
    json.dump(price_dump, f, indent=4)

print("✅ prices.json created successfully!")
