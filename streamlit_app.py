import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's TCG Tracker", page_icon="🎴", layout="wide")

# 2. The Multi-Result Scraper
def scoop_multi_results(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # This finds all product rows in the PriceCharting table
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
        
        card_data = []
        for row in rows:
            name = row.find('td', class_='title').text.strip()
            price = row.find('td', class_='numeric').text.strip()
            img_tag = row.find('img')
            img_url = img_tag['src'] if img_tag else None
            card_data.append({"name": name, "price": price, "img": img_url})
            
        return card_data
    except:
        return None

# 3. Memory Setup
if 'search_query' not in st.session_state:
    st.session_state.search_query = "Togedemaru 104"

# 4. Main Layout
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    card_name = st.text_input("Search a card", value=st.session_state.search_query)

    if card_name:
        with st.spinner(f'Scooping all versions of {card_name}...'):
            results = scoop_multi_results(card_name)
            
            if results:
                # If there's only one result, we make it big/prominent
                if len(results) == 1:
                    st.success("Found a direct match!")
                
                for res in results:
                    c1, c2, c3 = st.columns([1, 3, 1])
                    with c1:
                        if res['img']: st.image(res['img'], width=100)
                    with c2:
                        st.subheader(res['name'])
                    with c3:
                        st.write(f"### {res['price']}")
                    st.divider()
            else:
                st.error("No results found. Try checking the spelling or set number!")

with fav_col:
    st.markdown("### ⭐ Happyboy457’s favorites")
    st.info("Quick Search:")
    
    fav_list = ["Togedemaru 104", "Guzzlord gx sv71", "Scizor GX SV72", "zoroark gx 77a"]
    
    for fav in fav_list:
        if st.button(f"🔍 {fav}", key=f"f_{fav}", use_container_width=True):
            st.session_state.search_query = fav
            st.rerun()
