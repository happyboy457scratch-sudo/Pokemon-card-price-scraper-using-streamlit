import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. AUTH0 GATEKEEPER
# This checks if the user is authenticated via st.user
if not st.user.is_logged_in:
    st.title("🔒 TCG Price Tracker")
    st.info("Please log in to access the Pokémon price scraper.")
    if st.button("Log in with Google/Email"):
        st.login("auth0") # Matches your [auth.auth0] secrets
    st.stop()  # Important: This stops the scraper from running for guests

# --- EVERYTHING BELOW RUNS ONLY AFTER LOGIN ---

# 2. LOGGED-IN UI
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🎴 Pokémon Price Scraper")
with col2:
    if st.button("Log out"):
        st.logout()

st.write(f"Logged in as: **{st.user.name}**")
st.divider()

# 3. THE ORIGINAL SCRAPING LOGIC
def scrape_pokemon_data(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    
    # We use these headers to make the scraper look like a real person browsing
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        cards = []
        # Find the main results table
        table = soup.find("table", {"id": "main_table"})
        
        if table:
            rows = table.select("tr")[1:] # Skip the header row
            for row in rows[:5]: # Take top 5 results
                cols = row.find_all("td")
                if len(cols) >= 3:
                    name = cols[0].text.strip()
                    price = cols[2].text.strip()
                    
                    # Extract the image URL
                    img_tag = row.find("img")
                    img_url = img_tag.get("src") if img_tag else None
                    
                    cards.append({"Name": name, "Price": price, "Image": img_url})
        return cards
    except Exception as e:
        st.error(f"Scraper error: {e}")
        return []

# 4. APP INTERFACE
query = st.text_input("Enter Card Name:", placeholder="e.g. Charizard Base Set")

if st.button("Search Prices"):
    if query:
        with st.spinner("Scraping latest prices..."):
            results = scrape_pokemon_data(query)
            
            if results:
                for card in results:
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            if card["Image"]:
                                st.image(card["Image"], width=120)
                        with c2:
                            st.subheader(card["Name"])
                            st.metric("Ungraded Price", card["Price"])
            else:
                st.warning("No cards found. Try being more specific.")
