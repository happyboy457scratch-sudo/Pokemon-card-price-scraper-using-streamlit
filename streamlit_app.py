import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's TCG Tracker", page_icon="🎴", layout="wide")

# 2. Setup Permanent Folder for Images
IMG_DIR = "saved_images"
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# 3. The "Permanent Scooper" Function
@st.cache_data(ttl=3600)
def get_card_data(card_query):
    # Clean name for file saving
    clean_name = card_query.replace(' ', '_').replace('/', '-')
    filepath = os.path.join(IMG_DIR, f"{clean_name}.jpg")
    
    # Check if we already have the image saved locally
    has_local_img = os.path.exists(filepath)
    
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        card = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        
        if card:
            name = card.find('td', class_='title').text.strip()
            price = card.find('td', class_='numeric').text.strip()
            
            # If we don't have the image yet, download and save it
            if not has_local_img:
                img_tag = card.find('img')
                if img_tag and img_tag.get('src'):
                    img_url = img_tag['src']
                    img_data = requests.get(img_url).content
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
            
            return {"name": name, "price": price, "img": filepath}
    except Exception as e:
        # If web fails but we have a local image, show that
        if has_local_img:
            return {"name": card_query, "price": "Link Busy", "img": filepath}
    return None

# 4. Memory & History Setup
if 'history' not in st.session_state:
    st.session_state.history = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = "Togedemaru 104"

# 5. Sidebar (Left) - Recent Searches
with st.sidebar:
    st.title("🕒 Recent Searches")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            if st.button(item, key=f"hist_{item}", use_container_
