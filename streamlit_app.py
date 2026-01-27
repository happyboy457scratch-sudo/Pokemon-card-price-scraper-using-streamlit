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

st.title("🎴 Pokémon Card Finder")
st.write("Enter a name to see all versions of that card.")

# --- 3. REFINED CARD SEARCH ---
def get_all_card_versions(name):
    url = f"https://api.tcgdex.net/v2/en/cards?name={name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        
        results = response.json()
        detailed_cards = []
        
        # Pull the first 10 matches
        for item in results[:10]:
            detail_url = f"https://api.tcgdex.net/v2/en/cards/{item['id']}"
            card_data = requests.get(detail_url).json()
            
            detailed_cards.append({
                "name": card_data.get("name"),
                "set_name": card_data.get("set", {}).get("name"),
                "number": card_data.get("localId"),
                "rarity": card_data.get("rarity", "Common"),
                "image": f"{card_data.get('image')}/low.webp" if card_data.get('image') else None
            })
        return detailed_cards
    except Exception as e:
        return []

# --- 4. THE UI ---
query = st.text_input("Search for a card:", placeholder="e.g. Charizard")

if query:
    with st.spinner(f"Pulling versions of {query}..."):
        versions = get_all_card_versions(query)
        
        if versions:
            # We use a 2-column layout for a cleaner "Card Gallery" look
            cols = st.columns(2)
            for i, card in enumerate(versions):
                with cols[i % 2]:
                    with st.container(border=True):
                        if card["image"]:
                            st.image(card["image"], use_container_width=True)
                        st.subheader(card["name"])
                        st.write(f"**Set:** {card['set_name']}")
                        st.write(f"**Card #:** {card['number']}")
                        st.caption(f"Rarity: {card['rarity']}")
                        
                        # FIXED: This now matches the variable name above
                        search_term = f"{card['name']} {card['set_name']} {card['number']}".replace(" ", "+")
                        st.link_button("💰 Check PriceCharting", 
                                       f"https://www.pricecharting.com/search-products?q={search_term}&type=prices")
        else:
            st.warning("No specific cards found. Try a simpler name.")
