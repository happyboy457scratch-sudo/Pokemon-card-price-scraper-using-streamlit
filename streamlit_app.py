import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's Custom Tracker", page_icon="🎴", layout="wide")

# 2. Stable Multi-Result Scraper
def scoop_card_results(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
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
                        if res['img']: st.image(res['img'], width=120)
                    with c2:
                        st.subheader(res['name'])
                    with c3:
                        st.write(f"### {res['price']}")
                    st.divider()

with fav_col:
    st.markdown("### ⭐ My Real Collection")
    
    # Dictionary mapping card names to YOUR local filenames
    # Example: "Togedemaru 104": "togedemaru.png"
    my_photos = {
        "Togedemaru 104": "togedemaru.png",
        "Guzzlord GX SV71": "guzzlord.png",
        "Scizor GX SV72": "scizor.png",
        "Zoroark GX 77a": "zoroark.png"
    }
    
    for card_name, file_name in my_photos.items():
        photo_path = os.path.join("my_cards", file_name)
        
        # Check if your photo exists in the folder
        if os.path.exists(photo_path):
            st.image(photo_path, use_container_width=True, caption="Your Photo")
        else:
            st.caption(f"(Upload {file_name} to see your photo here)")
            
        if st.button(f"Search {card_name}", key=f"fav_{file_name}"):
            st.session_state.search_query = card_name
            st.rerun()
        st.write("---")
