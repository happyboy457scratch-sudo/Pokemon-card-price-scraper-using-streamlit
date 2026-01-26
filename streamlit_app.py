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
    clean_name = card_query.replace(' ', '_').replace('/', '-')
    filepath = os.path.join(IMG_DIR, f"{clean_name}.jpg")
    has_local_img = os.path.exists(filepath)
    
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        card = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        
        if card:
            name = card.find('td', class_='title').text.strip()
            price = card.find('td', class_='numeric').text.strip()
            
            if not has_local_img:
                img_tag = card.find('img')
                if img_tag and img_tag.get('src'):
                    img_data = requests.get(img_tag['src']).content
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
            
            return {"name": name, "price": price, "img": filepath}
    except Exception:
        if has_local_img:
            return {"name": card_query, "price": "Check Site", "img": filepath}
    return None

# 4. Memory Setup
if 'history' not in st.session_state:
    st.session_state.history = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = "Togedemaru 104"

# 5. Sidebar (Left) - Recent Searches
with st.sidebar:
    st.title("🕒 Recent Searches")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            # Shortened line to prevent cut-off
            if st.button(item, key=f"h_{item}"):
                st.session_state.search_query = item
                st.rerun()
    else:
        st.write("No history yet.")

# 6. Main Layout
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    card_name = st.text_input("Search a card", value=st.session_state.search_query)

    if card_name:
        if card_name not in st.session_state.history:
            st.session_state.history.append(card_name)
        
        with st.spinner('Scooping...'):
            res = get_card_data(card_name)
            if res:
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(res['img'], width=300)
                with c2:
                    st.header(res['name'])
                    st.subheader(f"Price: {res['price']}")
                
                st.components.v1.html(
                    "<script>window.parent.document.querySelector('section.main').scrollTo({top: 500, behavior: 'smooth'});</script>",
                    height=0
                )

with fav_col:
    st.markdown("### ⭐ Happyboy457’s favorites")
    fav_list = ["Togedemaru 104", "Guzzlord gx sv71", "Scizor GX SV72", "zoroark gx 77a"]
    
    for fav in fav_list:
        data = get_card_data(fav)
        if data:
            st.image(data['img'], use_container_width=True)
            st.write(f"**{data['name']}**")
            st.write(f"Price: {data['price']}")
            # Fixed button line
            if st.button(f"View {fav}", key=f"f_{fav}"):
                st.session_state.search_query = fav
                st.rerun()
        st.divider()
