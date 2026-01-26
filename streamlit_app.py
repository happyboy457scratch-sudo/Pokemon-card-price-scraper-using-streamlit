import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's TCG Tracker", page_icon="🎴", layout="wide")

# 2. Memory Setup (Session State)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# 3. Sidebar (Left Side) - Search History
with st.sidebar:
    st.title("🕒 Recent Searches")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            if st.button(item, key=f"hist_{item}", use_container_width=True):
                st.session_state.search_query = item
                st.rerun()
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.write("No history yet.")

# 4. Main App Layout (Split into 2 Columns)
# This creates the "Right Sidebar" effect for Favorites
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    
    # Input box - uses the session_state to allow favorites to "fill" it
    card_name = st.text_input("Enter Card Name", value=st.session_state.search_query)

    if card_name:
        # Add to history list
        if card_name not in st.session_state.history:
            st.session_state.history.append(card_name)
        
        with st.spinner(f'Searching for {card_name}...'):
            search_url = f"https://www.pricecharting.com/search-products?q={card_name.replace(' ', '+')}&type=prices"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            try:
                response = requests.get(search_url, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                cards = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
                
                if not cards:
                    st.warning("No cards found. Try a different name!")
                else:
                    for card in cards:
                        name = card.find('td', class_='title').text.strip()
                        price = card.find('td', class_='numeric').text.strip()
                        img_tag = card.find('img')
                        img_url = img_tag['src'] if img_tag else None

                        c1, c2, c3 = st.columns([1, 3, 1])
                        with c1:
                            if img_url: st.image(img_url, width=80)
                        with c2:
                            st.subheader(name)
                        with c3:
                            st.write(f"### {price}")
                        st.divider()

                    # --- AUTO-SCROLL JAVASCRIPT ---
                    # This tells the browser to scroll down after loading results
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
            except Exception as e:
                st.error(f"Error: {e}")

with fav_col:
    st.markdown("### ⭐ Happyboy457’s favorites")
    st.write("Click a card to check its current price:")
    
    my_favs = [
        "Togedemaru 104", 
        "Guzzlord gx sv71", 
        "Scizor GX SV72", 
        "zoroark gx 77a"
    ]
    
    for fav in my_favs:
        # If a favorite is clicked, update the search query and rerun
        if st.button(f"🔍 {fav}", key=f"fav_{fav}", use_container_width=True):
