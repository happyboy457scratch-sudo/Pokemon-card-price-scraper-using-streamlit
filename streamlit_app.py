import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- AUTH0 GATEKEEPER ---
if not st.user.is_logged_in:
    st.title("🔒 TCG Member Access")
    if st.button("Log in"):
        st.login("auth0")
    st.stop()

# --- SCRAPER WITH IMAGE SUPPORT ---
def scrape_pokemon_data(card_query):
    # Using PriceCharting as the example source
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        cards = []
        # Finding the rows in the results table
        rows = soup.select("table#main_table tr")[1:] 
        
        for row in rows[:5]: # Let's stick to top 5 results to keep it fast
            cols = row.find_all("td")
            if len(cols) > 1:
                name = cols[0].text.strip()
                price = cols[2].text.strip()
                
                # --- PICTURE LOGIC ---
                # We look for the image tag within the row
                img_tag = row.find("img")
                # Some sites use 'src', others use 'data-src' for lazy loading
                img_url = img_tag.get("src") if img_tag else None
                
                cards.append({
                    "Name": name, 
                    "Price": price, 
                    "Image": img_url
                })
        
        return cards
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# --- USER INTERFACE ---
st.title("🎴 Pokémon Card Price Scraper")
query = st.text_input("Search for a card:", placeholder="e.g. Pikachu VMAX")

if st.button("Search"):
    results = scrape_pokemon_data(query)
    
    if results:
        for card in results:
            # Create a clean layout for each card
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if card["Image"]:
                        st.image(card["Image"], width=150)
                    else:
                        st.write("No image found")
                
                with col2:
                    st.subheader(card["Name"])
                    st.metric("Market Price", card["Price"])
    else:
        st.warning("No results found. Try a different search.")
