import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's HD Collection", page_icon="🎴", layout="wide")

# 2. Scraper for Market Values
def scoop_market_price(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        card_row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if card_row:
            return card_row.find('td', class_='numeric').text.strip()
    except:
        return "N/A"
    return "N/A"

# 3. Sidebar/Favorites Data (Updated Queries for Accuracy)
my_collection = [
    {"name": "Reshiram GX", "id": "SV51/SV94", "image": "reshiram.jpg", "query": "Reshiram GX SV51"},
    {"name": "Scizor GX", "id": "SV72/SV94", "image": "scizor.jpg", "query": "Scizor GX SV72"},
    {"name": "Zoroark GX", "id": "77a/73", "image": "zoroark.jpg", "query": "Zoroark GX 77a"},
    {"name": "Togedemaru", "id": "104/094", "image": "togedemaru.jpg", "query": "Togedemaru 104"}
]

# 4. Main Layout
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 My Personal HD TCG Tracker")
    
    if 'selected_card' in st.session_state:
        selected = st.session_state.selected_card
        with st.spinner(f"Fetching market data for {selected['name']}..."):
            price = scoop_market_price(selected['query'])
            
            c1, c2 = st.columns([1, 2])
            with c1:
                # Displays the HD photo you uploaded
                st.image(selected['image'], use_container_width=True, caption=f"ID: {selected['id']}")
            with c2:
                st.header(selected['name'])
                st.subheader(f"Set ID: {selected['id']}")
                st.metric(label="Current Market Value", value=price)
                if st.button("Clear View"):
                    del st.session_state['selected_card']
                    st.rerun()
    else:
        st.info("Select a card from your favorites to view its HD art and live price.")

with fav_col:
    # UPDATED HEADING HERE
    st.markdown("### ⭐ Happyboy457’s Favorites")
    for card in my_collection:
        # Show your uploaded photo as a thumbnail
        if os.path.exists(card['image']):
            st.image(card['image'], use_container_width=True)
        else:
            st.warning(f"Missing: {card['image']}")
            
        if st.button(f"View {card['name']}", key=f"btn_{card['id']}", use_container_width=True):
            st.session_state.selected_card = card
            st.rerun()
        st.divider()
