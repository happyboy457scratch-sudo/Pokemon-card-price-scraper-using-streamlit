import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's Pro Tracker", page_icon="🎴", layout="wide")

# 2. Multi-Result Scraper
def scoop_multiple_cards(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
        
        results = []
        for row in rows[:3]: # Grab top 3 matches
            name = row.find('td', class_='title').text.strip()
            price = row.find('td', class_='numeric').text.strip()
            img_tag = row.find('img')
            img_url = img_tag['src'] if img_tag else None
            results.append({"name": name, "price": price, "img": img_url})
        return results
    except:
        return None

# 3. Sidebar/Favorites Data (Using your HD Photos)
my_collection = [
    {"name": "Reshiram GX", "id": "SV51/SV94", "image": "reshiram.jpg", "query": "Reshiram GX SV51"},
    {"name": "Scizor GX", "id": "SV72/SV94", "image": "scizor.jpg", "query": "Scizor GX SV72"},
    {"name": "Zoroark GX", "id": "77a/73", "image": "zoroark.jpg", "query": "Zoroark GX 77a"},
    {"name": "Togedemaru", "id": "104/094", "image": "togedemaru.jpg", "query": "Togedemaru 104"}
]

# 4. Layout Setup
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🔍 Pokémon Card Live Search")
    
    # The Search Bar (Back by popular demand!)
    search_input = st.text_input("Search any card on the internet (e.g. 'Charizard Base Set')", placeholder="Type here...")
    
    if search_input:
        with st.spinner(f"Searching for {search_input}..."):
            results = scoop_multiple_cards(search_input)
            if results:
                st.subheader(f"Results for '{search_input}':")
                for res in results:
                    c1, c2, c3 = st.columns([1, 3, 1])
                    with c1:
                        if res['img']: st.image(res['img'], width=100)
                    with c2:
                        st.write(f"**{res['name']}**")
                    with c3:
                        st.write(f"### {res['price']}")
                    st.divider()
            else:
                st.error("No cards found. Check your spelling!")
    else:
        st.info("👆 Use the search bar above to look up any card, or click a favorite on the right!")

with fav_col:
    st.markdown("### ⭐ Happyboy457’s Favorites")
    for card in my_collection:
        # Uses your high-res uploaded photos
        if os.path.exists(card['image']):
            st.image(card['image'], use_container_width=True)
        
        # This button puts the favorite into the search bar
        if st.button(f"Scoop Price: {card['name']}", key=f"btn_{card['id']}", use_container_width=True):
            # This triggers a live search for the specific favorite
            st.session_state.search_query = card['query']
            # We use a little trick to fill the search box
            # By rerunning, the main search logic will pick this up
            st.rerun()
        st.divider()
