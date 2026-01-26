import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's TCG Tracker", page_icon="🎴", layout="wide")

# 2. Setup Permanent Folder
IMG_DIR = "saved_images"
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# 3. The Permanent Scooper
@st.cache_data(ttl=3600) # Only refresh from web once per hour
def get_card_data(card_query):
    # Clean name for file saving (e.g., "Togedemaru_104.jpg")
    filename = f"{card_query.replace(' ', '_')}.jpg"
    filepath = os.path.join(IMG_DIR, filename)
    
    # --- STEP 1: Check if we already have it in the system ---
    if os.path.exists(filepath):
        return {"name": card_query, "img": filepath, "is_local": True}
    
    # --- STEP 2: If not, scoop it from the web ---
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        card = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        
        if card:
            name = card.find('td', class_='title').text.strip()
            price = card.find('td', class_='numeric').text.strip()
            img_url = card.find('img')['src'] if card.find('img') else None
            
            # --- STEP 3: Save the picture to the system ---
            if img_url:
                img_data = requests.get(img_url).content
                with open(filepath, 'wb') as f:
                    f.write(img_data)
            
            return {"name": name, "price": price, "img": filepath, "is_local": False}
    except:
        return None
    return None

# 4. Main Layout & Logic
if 'search_query' not in st.session_state:
    st.session_state.search_query = "Togedemaru 104"

main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    card_name = st.text_input("Search a card", value=st.session_state.search_query)

    if card_name:
        with st.spinner('Checking system memory...'):
            res = get_card_data(card_name)
            if res:
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(res['img'], width=300)
                with c2:
                    st.header(res['name'])
                    # If it's local, we might need to scoop just the price again
                    st.subheader(f"Price: {res.get('price', 'Check Favorites')}")
            else:
                st.error("Card not found.")

with fav_col:
    st.markdown("### ⭐ Happyboy457’s favorites")
    fav_list = ["Togedemaru 104", "Guzzlord gx sv71", "Scizor GX SV72", "zoroark gx 77a"]
    
    for fav in fav_list:
