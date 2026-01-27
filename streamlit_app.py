import streamlit as st
import requests

# --- 1. THE ACCOUNT PART (Auth0 Gatekeeper) ---
if not st.user.is_logged_in:
    st.title("⚡Pokemon Card Price Tracker⚡")
    st.info("Log in to use the price tracker, we won't send you any spam.")
    if st.button("Log In with google or email!"):
        st.login("auth0")
    st.stop()

# --- 2. USER DASHBOARD (Sidebar) ---
with st.sidebar:
    st.success(f"Trainer: {st.user.name}")
    st.write(f"Email: {st.user.email}")
    if st.button("Logout"):
        st.logout()

st.title("🎴 Pokémon Price Hub")
st.write("Search for specific cards to see their real-time market value.")

# --- 3. THE DATA ENGINE (TCGdex API + Smart Pricing) ---
def get_card_data(name):
    # Search for cards by name
    search_url = f"https://api.tcgdex.net/v2/en/cards?name={name}"
    try:
        response = requests.get(search_url, timeout=10)
        results = response.json()
        
        all_cards = []
        # Get detailed info for the top 10 matches
        for item in results[:10]:
            detail_url = f"https://api.tcgdex.net/v2/en/cards/{item['id']}"
            card = requests.get(detail_url).json()
            
            # --- SMART PRICE SEARCH ---
            tcg_data = card.get("pricing", {}).get("tcgplayer", {})
            market_price = "N/A"
            
            if tcg_data:
                # Loop through possible print variants to find the first valid price
                # Umbreon VMAX is usually 'holofoil', while base cards are 'normal'
                for p_type in ["holofoil", "normal", "reverse", "unlimited"]:
                    p_info = tcg_data.get(p_type)
                    if p_info and p_info.get("market"):
                        market_price = f"${p_info.get('market')}"
                        break 
            
            all_cards.append({
                "name": card.get("name"),
                "set": card.get("set", {}).get("name"),
                "number": card.get("localId"),
                "image": f"{card.get('image')}/low.webp" if card.get('image') else None,
                "price": market_price,
                "rarity": card.get("rarity", "Common")
            })
        return all_cards
    except Exception as e:
        return []

# --- 4. THE APP INTERFACE ---
query = st.text_input("Enter Card Name:", placeholder="e.g. Umbreon VMAX")

if query:
    with st.spinner(f"Analyzing market for {query}..."):
        cards = get_card_data(query)
        
        if cards:
            # Display cards in a 2-column grid
            cols = st.columns(2)
            for i, card in enumerate(cards):
                with cols[i % 2]:
                    with st.container(border=True):
                        if card["image"]:
                            st.image(card["image"], use_container_width=True)
                        
                        st.subheader(card["name"])
                        
                        # Show the Market Price in a big metric box
                        st.metric("Market Value", card["price"])
                        
                        st.write(f"**Set:** {card['set']}")
                        st.write(f"**Card #:** {card['number']}")
                        st.caption(f"Rarity: {card['rarity']}")
                        
                        # Direct PriceCharting Link for historical data
                        search_term = f"{card['name']} {card['set']} {card['number']}".replace(" ", "+")
                        st.link_button("View Price History", 
                                       f"https://www.pricecharting.com/search-products?q={search_term}&type=prices")
        else:
            st.warning("No specific card variants found. Try adding the set name!")
