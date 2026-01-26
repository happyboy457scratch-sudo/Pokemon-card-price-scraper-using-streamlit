import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="TCG Price Tracker", page_icon="🎴")

# --- MEMORY (SESSION STATE) SETUP ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR FOR RECENT SEARCHES ---
st.sidebar.title("🕒 Recent Searches")
if st.session_state.history:
    for item in reversed(st.session_state.history):
        if st.sidebar.button(item, key=f"btn_{item}"):
            # This makes clicking a history item search for it again
            st.rerun() 
else:
    st.sidebar.write("No searches yet!")

if st.sidebar.button("Clear History"):
    st.session_state.history = []
    st.rerun()

# --- MAIN APP INTERFACE ---
st.title("🎴 Pokémon Card Price Finder")

card_name = st.text_input("Card Name (e.g. Mewtwo GX)", "")

if card_name:
    # Add to history if it's a new search
    if card_name not in st.session_state.history:
        st.session_state.history.append(card_name)
        # Keep only the last 10 searches
        if len(st.session_state.history) > 10:
            st.session_state.history.pop(0)

    with st.spinner('Fetching cards and images...'):
        search_url = f"https://www.pricecharting.com/search-products?q={card_name.replace(' ', '+')}&type=prices"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            cards = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
            
            if not cards:
                st.warning("No cards found. Try being more specific.")
            else:
                for card in cards:
                    name = card.find('td', class_='title').text.strip()
                    price = card.find('td', class_='numeric').text.strip()
                    img_tag = card.find('img')
                    img_url = img_tag['src'] if img_tag else None

                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        if img_url: st.image(img_url, width=100)
                    with col2:
                        st.write(f"### {name}")
                    with col3:
                        st.write(f"## {price}")
                    st.divider()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
