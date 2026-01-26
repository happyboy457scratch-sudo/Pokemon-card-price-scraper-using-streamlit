import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="TCG Price Tracker", page_icon="🎴", layout="wide")

# --- MEMORY SETUP ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- FAVORITES LIST ---
favorites = [
    "Togedemaru 104", 
    "Guzzlord gx sv71", 
    "Scizor GX SV72", 
    "zoroark gx 77a"
]

# --- SIDEBAR (LEFT) ---
with st.sidebar:
    st.title("🕒 Recent Searches")
    for item in reversed(st.session_state.history):
        if st.button(item, key=f"hist_{item}"):
            st.session_state.search_trigger = item
            st.rerun()
    
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# --- MAIN LAYOUT (Creating a 'Right' Side) ---
# We split the screen into two columns: 3/4 for search, 1/4 for favorites
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    
    # Use a key to allow sidebar buttons to fill this box
    search_val = st.session_state.get('search_trigger', "")
    card_name = st.text_input("Card Name (e.g. Charizard)", value=search_val)

    if card_name:
        if card_name not in st.session_state.history:
            st.session_state.history.append(card_name)
        
        with st.spinner('Scraping prices...'):
            url = f"https://www.pricecharting.com/search-products?q={card_name.replace(' ', '+')}&type=prices"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            cards = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))

            if not cards:
                st.warning("No cards found.")
            else:
                for card in cards:
                    name = card.find('td', class_='title').text.strip()
                    price = card.find('td', class_='numeric').text.strip()
                    img_url = card.find('img')['src'] if card.find('img') else None
                    
                    c1, c2, c3 = st.columns([1, 2, 1])
                    if img_url: c1.image(img_url, width=80)
                    c2.write(f"**{name}**")
                    c3.write(f"`{price}`")
                
                # --- AUTO-SCROLL TRICK ---
                # This injects a tiny bit of Javascript to scroll to the bottom
                st.components.v1.html(
                    """
                    <script>
                        window.parent.document.querySelector('section.main').scrollTo({
                            top: window.parent.document.querySelector('section.main').scrollHeight,
                            behavior: 'smooth'
                        });
                    </script>
                    """,
                    height=0,
                )

with fav_col:
    st.markdown("### ⭐ My Favorites")
    st.info("Click to search quickly!")
    for fav in favorites:
        if st.button(f"🔍 {fav}", key=f"fav_{fav}", use_container_width=True):
            st.session_state.search_trigger = fav
            st.rerun()
