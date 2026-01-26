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

# 3. The "Stealth Scooper" Function
@st.cache_data(ttl=3600)
def get_card_data(card_query):
    clean_name = card_query.replace(' ', '_').replace('/', '-')
    filepath = os.path.join(IMG_DIR, f"{clean_name}.jpg")
    
    # Use a more advanced User-Agent to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the table row for the product
        card = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        
        if card:
            name = card.find('td', class_='title').text.strip()
            price = card.find('td', class_='numeric').text.strip()
            
            # Check if we need to save the image locally
            if not os.path.exists(filepath):
                img_tag = card.find('img')
                if img_tag and img_tag.get('src'):
                    img_res = requests.get(img_tag['src'], headers=headers)
                    with open(filepath, 'wb') as f:
                        f.write(img_res.content)
            
            return {"name": name, "price": price, "img": filepath}
    except Exception as e:
        if os.path.exists(filepath):
            return {"name": card_query, "price": "Site Busy", "img": filepath}
    return None

# 4. Memory & History
if 'history' not in st.session_state:
    st.session_state.history = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = "Togedemaru 104"

# 5. Sidebar
with st.sidebar:
    st.title("🕒 Recent")
    if st.button("Clear App Memory"):
        st.cache_data.clear()
        st.rerun()
    for item in reversed(st.session_state.history):
        if st.button(item, key=f"h_{item}"):
            st.session_state.search_query = item
            st.rerun()

# 6. Main Layout
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    card_name = st.text_input("Search a card", value=st.session_state.search_query)

    if card_name:
        if card_name not in st.session_state.history:
            st.session_state.history.append(card_name)
        
        with st.spinner('Scooping live data...'):
            res = get_card_data(card_name)
            if res:
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(res['img'], width=300)
                with c2:
                    st.header(res['name'])
                    st.subheader(f"Price: {res['price']}")
            else:
                st.error("The website is blocking us or the card doesn't exist. Try searching again in 30 seconds.")

with fav_col:
    st.markdown("### ⭐ Happyboy457’s favorites")
    fav_list = ["Togedemaru 104", "Guzzlord gx sv71", "Scizor GX SV72", "zoroark gx 77a"]
    
    for fav in fav_list:
        data = get_card_data(fav)
        if data:
            st.image(data['img'], use_container_width=True)
            st.write(f"**{data['name']}**")
            st.write(f"Price: {data['price']}")
            if st.button(f"View {fav}", key=f"f_{fav}"):
                st.session_state.search_query = fav
                st.rerun()
        else:
            st.write(f"⏳ Loading {fav}...")
        st.divider()
