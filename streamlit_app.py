import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's TCG Tracker", page_icon="🎴", layout="wide")

# 2. Memory Setup
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. Sidebar (Left Side) - Search History
with st.sidebar:
    st.title("🕒 Recent Searches")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            if st.button(item, key=f"hist_{item}", use_container_width=True):
                st.session_state.search_query = item
                st.rerun()
    else:
        st.write("No history yet.")

# 4. Main Layout
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    
    # --- AUTO-LOAD LOGIC ---
    # If this is the first time opening the app, set default to your favorite
    if 'search_query' not in st.session_state:
        st.session_state.search_query = "Togedemaru 104"
    
    card_name = st.text_input("Enter Card Name", value=st.session_state.search_query)

    if card_name:
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
                    st.warning("No cards found.")
                else:
                    for card in cards:
                        name = card.find('td', class_='title').text.strip()
                        price = card.find('td', class_='numeric').text.strip()
                        img_tag = card.find('img')
                        img_url = img_tag['src'] if img_tag else None

                        c1, c2, c3 = st.columns([1, 3, 1])
                        with c1:
                            if img_url: st.image(img_url, width=120)
                        with c2:
                            st.subheader(name)
                        with c3:
                            st.write(f"### {price}")
                        st.divider()

                    # Auto-Scroll Script
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
    
    # Manually verified high-quality image links
    my_favs = {
        "Togedemaru 104": "https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/sm6/104.png",
        "Guzzlord GX SV71": "https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/sm8b/SV71.png",
        "Scizor GX SV72": "https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/sm8b/SV72.png",
        "Zoroark GX 77a": "https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/sm35/77a.png"
    }
    
    for name, img_url in my_favs.items():
        st.image(img_url, use_container_width=True)
        if st.button(f"Search {name}", key=f"fav_btn_{name}", use_container_width=True):
            st.session_state.search_query = name
            st.rerun()
        st.write("---")
