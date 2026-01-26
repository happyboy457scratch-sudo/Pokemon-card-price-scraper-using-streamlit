import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's HD Tracker", page_icon="🎴", layout="wide")

# 2. HD Scooper Function
def get_card_data_hd(card_query):
    # --- Step 1: Get Price from PriceCharting ---
    pc_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    price = "N/A"
    pc_name = card_query
    
    try:
        pc_res = requests.get(pc_url, headers=headers, timeout=10)
        soup = BeautifulSoup(pc_res.content, 'html.parser')
        card_row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if card_row:
            pc_name = card_row.find('td', class_='title').text.strip()
            price = card_row.find('td', class_='numeric').text.strip()
    except:
        pass

    # --- Step 2: Get HD Image from Pokémon TCG API ---
    # We search the official API using the card name
    api_url = f"https://api.pokemontcg.io/v2/cards?q=name:\"{card_query.split(' ')[0]}\""
    img_url = None
    
    try:
        api_res = requests.get(api_url, timeout=10).json()
        if api_res['data']:
            # We try to find the best match in the API results
            img_url = api_res['data'][0]['images']['large']
    except:
        pass
        
    return {"name": pc_name, "price": price, "img": img_url}

# 3. Memory Setup
if 'search_query' not in st.session_state:
    st.session_state.search_query = "Togedemaru 104"

# 4. Layout
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("✨ HD Pokémon Card Finder")
    card_name = st.text_input("Search a card", value=st.session_state.search_query)

    if card_name:
        with st.spinner('Fetching HD Art...'):
            res = get_card_data_hd(card_name)
            c1, c2 = st.columns([1, 2])
            with c1:
                if res['img']: 
                    st.image(res['img'], caption="Official HD Scan")
                else:
                    st.warning("HD Image not found, showing price only.")
            with c2:
                st.header(res['name'])
                st.subheader(f"Current Market Price: {res['price']}")

with fav_col:
    st.markdown("### ⭐ Favorites")
    favs = ["Togedemaru 104", "Guzzlord GX SV71", "Scizor GX SV72", "Zoroark GX 77a"]
    for fav in favs:
        if st.button(f"🔍 {fav}", key=f"f_{fav}", use_container_width=True):
            st.session_state.search_query = fav
            st.rerun()
