import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's HD Collection", page_icon="🎴", layout="wide")

# 2. Scraper for Market Values
@st.cache_data(ttl=3600) # Cache prices for 1 hour to stay fast
def scoop_market_price(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        card_row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if card_row:
            price_text = card_row.find('td', class_='numeric').text.strip()
            # Clean the price string (remove $ and ,) to turn it into a number
            return price_text
    except:
        return "$0.00"
    return "$0.00"

# 3. Sidebar/Favorites Data
my_collection = [
    {"name": "Reshiram GX", "id": "SV51/SV94", "image": "reshiram.jpg", "query": "Reshiram GX SV51"},
    {"name": "Scizor GX", "id": "SV72/SV94", "image": "scizor.jpg", "query": "Scizor GX SV72"},
    {"name": "Zoroark GX", "id": "77a/73", "image": "zoroark.jpg", "query": "Zoroark GX 77a"},
    {"name": "Togedemaru", "id": "104/094", "image": "togedemaru.jpg", "query": "Togedemaru 104"}
]

# --- NEW: Calculate Total Collection Value ---
def get_total_value():
    total = 0.0
    for card in my_collection:
        price_str = scoop_market_price(card['query'])
        try:
            # Convert "$12.34" -> 12.34
            clean_price = float(price_str.replace('$', '').replace(',', ''))
            total += clean_price
        except:
            continue
    return total

# 4. Main Layout
main_col, fav_col = st.columns([3, 1], gap="large")
