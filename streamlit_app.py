import streamlit as st
import requests

# --- 1. THE ACCOUNT PART ---
if not st.user.is_logged_in:
    st.title("🔒 Trainer Access Only")
    if st.button("Log In"):
        st.login("auth0")
    st.stop()

# --- 2. USER DASHBOARD ---
with st.sidebar:
    st.success(f"Hello, {st.user.name}!")
    if st.button("Logout"):
        st.logout()

st.title("🎴 Pokémon Price & Card Finder")
st.write("Search for a card to see the art and real-time market values.")

# --- 3. THE DATA PART (With Prices) ---
def get_card_data(name):
    # Step A: Search for cards by name
    search_url = f"https://api.tcgdex.net/v2/en/cards?name={name}"
    try:
        response = requests.get(search_url, timeout=10)
        results = response.json()
        
        all_cards = []
        # Get detailed info for the top 8 matches
        for item in results[:8]:
            detail_url = f"https://api.tcgdex.net/v2/en/cards/{item['id']}"
            card = requests.get(detail_url).json()
            
            # Extract Pricing (TCGplayer data is nested here)
            pricing = card.get("variants", {})
            # We look for 'normal' or 'holofoil' market prices
            tcg_data = card.get("pricing", {}).get("tcgplayer", {})
            market_price = "N/A"
            
            # Check for different price types (Normal, Holo, Reverse)
            if tcg_data:
                # Prioritize Holofoil price, then Normal
                p_obj = tcg_data.get("holofoil") or tcg_data.get("normal") or tcg_data.get("reverse")
                if p_obj:
                    market_price = f"${p_obj.get('market', 'N/A')}"

            all_cards.append({
                "name": card.get("name"),
                "set": card.get("set", {}).get("name"),
                "number": card.get("localId"),
                "image": f"{card.get('image')}/low.webp" if card.get('image') else None,
                "price": market_price,
                "rarity": card.get("rarity")
            })
        return all_cards
    except:
        return []

# --- 4. THE INTERFACE ---
query = st.text_input("Enter Card Name:", placeholder="e.g. Umbreon VMAX")

if query:
    with st.spinner(f"Fetching market data for {query}..."):
        cards = get_card_data(query)
        
        if cards:
            cols = st.columns(2)
            for i, card in enumerate(cards):
                with cols[i % 2]:
                    with st.container(border=True):
                        if card["image"]:
                            st.image(card["image"])
                        st.subheader(card["name"])
                        
                        # DISPLAY THE PRICE
                        st.metric("Market Price (TCGplayer)", card["price"])
                        
                        st.write(f"**Set:** {card['set']} (#{card['number']})")
                        st.caption(f"Rarity: {card['rarity']}")
                        
                        # Backup link to PriceCharting if they want more history
                        search_term = f"{card['name']} {card['set']} {card['number']}".replace(" ", "+")
                        st.link_button("View Price History", 
                                       f"https://www.pricecharting.com/search-products?q={search_term}&type=prices")
        else:
            st.warning("No specific cards found. Try including the set name!")
