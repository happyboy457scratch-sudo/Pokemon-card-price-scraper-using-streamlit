import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's TCG Tracker", page_icon="🎴", layout="wide")

# 2. Stable Multi-Result Scraper
def scoop_card_results(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
        
        results = []
        for row in rows:
            name = row.find('td', class_='title').text.strip()
            price = row.find('td', class_='numeric').text.strip()
            img_tag = row.find('img')
            img_url = img_tag['src'] if img_tag else None
            results.append({"name": name, "price": price, "img": img_url})
        return results
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
        with st.spinner(f'Scooping results for {card_name}...'):
            results = scoop_card_results(card_name)
            
            if results:
                for res in results:
                    c1, c2, c3 = st.columns([1, 3, 1])
                    with c1:
                        # This line is indented 4 spaces inside with c1
                        if res['img']: 
                            st.image(res['img'], width=120)
                    with c2:
                        # This line is indented 4 spaces inside with c2
                        st.subheader(res['name'])
                    with c3:
                        # FIXED: This line was likely missing or not indented
                        st.write(f"### {res['price']}")
                    st.divider()
            else:
                st.error("No results found. The site might be busy!")

with fav_col:
    st.markdown("### ⭐ Happyboy457’s favorites")
    fav_list = ["Togedemaru 104", "Guzzlord GX SV71", "Scizor GX SV72", "Zoroark GX 77a"]
    
    for fav in fav_list:
        if st.button(f"🔍 Search {fav}", key=f"fav_{fav}", use_container_width=True):
            st.session_state.search_query = fav
            st.rerun()
