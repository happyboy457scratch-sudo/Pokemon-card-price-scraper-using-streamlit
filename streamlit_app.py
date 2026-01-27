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

st.title("🎴 Specific Pokémon Card Finder")
st.write("Enter a name to see every version of that card (Set, Number, and Rarity).")

# --- 3. REFINED CARD SEARCH ---
def get_all_card_versions(name):
    # This searches the database for specific card instances
    url = f"https://api.tcgdex.net/v2/en/cards?name={name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        
        # This returns a list of unique card IDs (e.g., 'swsh12-1', 'base1-4')
        results = response.json()
        
        detailed_cards = []
        # We'll grab the first 12 versions found to keep the page clean
        for item in results[:12]:
            # Get the full details for EACH unique card ID
            detail_url = f"https://api.tcgdex.net/v2/en/cards/{item['id']}"
            card_data = requests.get(detail_url).json()
            
            detailed_cards.append({
                "name": card_data.get("name"),
                "set_name": card_data.get("set", {}).get("name"),
                "number": card_data.get("localId"),
                "rarity": card_data.get("rarity"),
                "image": f"{card_data.get('image')}/low.webp" if card_data.get('image') else None
            })
        return detailed_cards
    except:
        return []

# --- 4. THE UI ---
query = st.text_input("Search for a specific card:", placeholder="e.g. Charizard")

if query:
    with st.spinner(f"Pulling every version of {query}..."):
        versions = get_all_card_versions(query)
        
        if versions:
            # Create a grid layout for the cards
            cols = st.columns(2)
            for i, card in enumerate(versions):
                with cols[i % 2]: # Alternates between left and right column
                    with st.container(border=True):
                        if card["image"]:
                            st.image(card["image"])
                        st.subheader(card["name"])
                        st.write(f"**Set:** {card['set_name']}")
                        st.write(f"**Card #:** {card['number']}")
                        st.write(f"**Rarity:** {card['rarity']}")
                        
                        # Direct Price Link for this specific version
                        search_term = f"{card['name']} {card['set_name']} {card['number']}".replace(" ", "+")
                        st.link_button("💰 Check Market Price", 
                                       f"https://www.pricecharting.com/search-products?q={search_query}&type=prices")
        else:
            st.warning("No specific cards found with that name.")
