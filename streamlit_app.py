import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import time

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's TCG Tracker", page_icon="🎴", layout="wide")

# 2. Setup Permanent Folder
IMG_DIR = "saved_images"
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# 3. The Polite Scooper
# Cache is now 24 hours (86400s) to minimize hitting the site
@st.cache_data(ttl=86400)
def get_card_data(card_query):
    clean_name = card_query.replace(' ', '_').replace('/', '-')
    filepath = os.path.join(IMG_DIR, f"{clean_name}.jpg")
    
    # Check if we have it locally FIRST (No delay needed if we have it)
    if os.path.exists(filepath):
        # We still need to scoop the price if we want it live, 
        # but let's assume if it's cached, we skip the wait.
        pass

    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # --- THE DELAY ---
        # We wait 10 seconds before the actual request
        time.sleep(10) 
        
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        card = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        
        if card:
            name = card.find('td', class_='title').text.strip()
            price = card.find('td', class_='numeric').text.strip()
            
            if not os.path.exists(filepath):
                img_tag = card.find('img')
                if img_tag and img_tag.get('src'):
                    img_data = requests.get(img_tag['src']).content
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
            
            return {"name": name, "price": price, "img": filepath}
    except:
        return None
    return None

# 4. Main App Logic
if 'search_query' not in st.session_state:
    st.session_state.search_query = "Togedemaru 104"

main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    card_name = st.text_input("Search a card", value=st.session_state.search_query)

    if card_name:
        with st.status(f"Scooping {card_name}...", expanded=True) as status:
            st.write("Waiting 10s to stay under the radar...")
            res = get_card_data(card_name)
            if res:
                status.update(label="Data Secured!", state="complete")
                c1, c2 = st.columns([1, 2])
                with c1:
