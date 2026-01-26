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
@st.cache_data(ttl=86400)
def get_card_data(card_query):
    clean_name = card_query.replace(' ', '_').replace('/', '-')
    filepath = os.path.join(IMG_DIR, f"{clean_name}.jpg")
    
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # Polite 10-second delay
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
                    # INDENTED PROPERLY
                    st.image(res['img'], width=300)
                with c2:
                    # INDENTED PROPERLY
                    st.header(res['name'])
                    st.subheader(f"Price: {res['price']}")
            else:
                status.update(label="Scoop Failed", state="error")

with fav_col:
    st.markdown("### ⭐ Happyboy457’s favorites")
    fav_list = ["Togedemaru 104", "Guzzlord gx sv71", "Scizor GX SV72", "zoroark gx 77a"]
    
    for fav in fav_list:
        clean_fav = fav.replace(' ', '_').replace('/', '-')
        fav_path = os.path.join(IMG_DIR, f"{clean_fav}.jpg")
        
        if os.path.exists(fav_path):
            st.image(fav_path, use_container_width=True)
            st.write(f"**{fav}**")
            if st.button(f"Update {fav}", key=f"f_{fav}"):
                st.session_state.search_query = fav
                st.rerun()
        else:
            st.warning(f"Not in system.")
            if st.button(f"Fetch {fav}", key=f"fetch_{fav}"):
                st.session_state.search_query = fav
                st.rerun()
        st.divider()
