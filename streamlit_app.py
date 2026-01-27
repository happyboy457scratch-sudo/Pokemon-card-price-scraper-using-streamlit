import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. AUTHENTICATION CHECK (The Gatekeeper)
# This section ensures that if you aren't logged in, 
# the rest of the script NEVER runs.
if not st.user.is_logged_in:
    st.title("🔒 TCG Price Checker")
    st.write("Welcome! Please log in with your Google account to access the scraper.")
    
    # This triggers the login flow using the secrets you saved
    if st.button("Log in with Google"):
        st.login("google")
    
    # MANDATORY: Stop execution so the scraper doesn't try to load
    st.stop()

# --- EVERYTHING BELOW ONLY RUNS AFTER SUCCESSFUL LOGIN ---

# 2. APP HEADER & LOGOUT
st.set_page_config(page_title="Pokémon Price Scraper", page_icon="🎴")

col1, col2 = st.columns([4, 1])
with col1:
    st.title("🎴 Pokémon Card Price Scraper")
    st.write(f"Hello, **{st.user.name}**! Happy hunting.")
with col2:
    if st.button("Log out"):
        st.logout()

st.divider()

# 3. SCRAPER LOGIC
# Example scraper for PriceCharting or similar TCG sites
card_query = st.text_input("Enter Card Name (e.g., Charizard Base Set):", placeholder="Charizard...")

if st.button("Search Prices"):
    if card_query:
        with st.spinner(f"Searching for '{card_query}'..."):
            try:
                # Clean the query for the URL
                search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
                
                header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                response = requests.get(search_url, headers=header)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # This logic depends on the specific site's HTML structure
                # This is a generic example of finding a table of results
                results = []
                table = soup.find('table', {'id': 'products_table'})
                
                if table:
                    rows = table.find_all('tr')[1:] # Skip header
                    for row in rows:
                        name = row.find('td', {'class': 'title'}).text.strip()
                        price = row.find('td', {'class': 'price'}).text.strip()
                        results.append({"Card Name": name, "Current Price": price})
                    
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("No cards found. Try being more specific (e.g., 'Pikachu 58/102').")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a card name first.")

# 4. FOOTER
st.info("Note: Scraper results depend on the live data from the TCG provider.")
