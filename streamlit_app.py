import streamlit as st
import requests

# --- 1. THE ACCOUNT PART (Gatekeeper) ---
if not st.user.is_logged_in:
    st.title("🔒 Trainer Access Only")
    st.info("Please log in to use the Pokémon Card Finder.")
    if st.button("Log In"):
        st.login("auth0")
    st.stop()

# --- 2. USER DASHBOARD ---
with st.sidebar:
    st.success(f"Hello, {st.user.name}!")
    if st.button("Logout"):
        st.logout()

st.title("🎴 Pokémon Card Hub")
st.write("Enter a card name below to see the art and set details.")

# --- 3. THE DATA PART (Using TCGdex API) ---
def search_pokemon_cards(name):
    # This URL searches the official TCGdex database
    url = f"https://api.tcgdex.net/v2/en/cards?name={name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        
        results = response.json()
        cards_found = []
        
        # We grab the first 5 matches to keep it fast
        for item in results[:5]:
            # Fetch specific details for each card found
            detail_url = f"https://api.tcgdex.net/v2/en/cards/{item['id']}"
            card = requests.get(detail_url).json()
            
            cards_found.append({
                "name": card.get("name"),
                "set": card.get("set", {}).get("name"),
                "image": f"{card.get('image')}/low.webp",
                "rarity": card.get("rarity", "Standard")
            })
        return cards_found
    except:
        return []

# --- 4. THE INTERFACE ---
query = st.text_input("Search for a card:", placeholder="e.g. Charizard")

if query:
    with st.spinner(f"Finding {query}..."):
        cards = search_pokemon_cards(query)
        
        if cards:
            for card in cards:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(card["image"], use_container_width=True)
                    with col2:
                        st.header(card["name"])
                        st.write(f"**Set:** {card['set']}")
                        st.write(f"**Rarity:** {card['rarity']}")
                        
                        # Add a quick link to PriceCharting for the values
                        link_name = f"{card['name']} {card['set']}".replace(" ", "+")
                        st.link_button("View Prices on PriceCharting", 
                                       f"https://www.pricecharting.com/search-products?q={link_name}&type=prices")
        else:
            st.warning("No cards found. Try a simpler name like 'Pikachu'.")
