import streamlit as st
import requests

# --- 1. THE ACCOUNT PART (Gatekeeper) ---
# This checks if the user is logged in via Auth0
if not st.user.is_logged_in:
    st.title("🔒 Trainer Access Only")
    st.write("Please log in to use the Pokémon Price & Card Finder.")
    
    # This button triggers the Auth0 screen
    if st.button("Log In"):
        st.login("auth0")
    
    # This STOPS the scraper code from running until they log in
    st.stop()

# --- 2. THE USER DASHBOARD ---
# Now that we're past st.stop(), we know the user is logged in
st.sidebar.success(f"Welcome back, {st.user.name}!")
if st.sidebar.button("Logout"):
    st.logout()

st.title("🎴 Pokémon Card Hub")
st.write("Search for any card to see its details and market value.")

# --- 3. THE DATA PART (API instead of Scraping) ---
# We use TCGdex because regular scrapers get blocked on the cloud
def get_card_details(name):
    url = f"https://api.tcgdex.net/v2/en/cards?name={name}"
    try:
        # Search for cards
        response = requests.get(url).json()
        if not response:
            return None
        
        # Get full info for the first match
        card_id = response[0]['id']
        details = requests.get(f"https://api.tcgdex.net/v2/en/cards/{card_id}").json()
        return details
    except:
        return None

# --- 4. THE INTERFACE ---
query = st.text_input("Enter Card Name:", placeholder="e.g. Mewtwo")

if query:
    data = get_card_details(query)
    if data:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display high-quality image from the API
            img_url = f"{data.get('image')}/high.webp"
            st.image(img_url)
            
        with col2:
            st.header(data.get('name'))
            st.write(f"**Set:** {data.get('set', {}).get('name')}")
            st.write(f"**Rarity:** {data.get('rarity')}")
            
            # Since PriceCharting blocks scrapers, we show the official Rarity 
            # and a direct link to check live prices safely.
            search_query = data.get('name').replace(' ', '+')
            st.link_button("View Live Market Prices", 
                           f"https://www.pricecharting.com/search-products?q={search_query}&type=prices")
    else:
        st.warning("Card not found. Try checking your spelling!")
