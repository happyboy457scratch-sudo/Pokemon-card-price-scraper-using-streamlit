import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Happyboy457's TCG Tracker", page_icon="🎴", layout="wide")

# 2. The "Scooper" Function
# This function does the heavy lifting for the favorites bar
def scoop_card_data(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Get the first result row
        card = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if card:
            name = card.find('td', class_='title').text.strip()
            price = card.find('td', class_='numeric').text.strip()
            img_url = card.find('img')['src'] if card.find('img') else None
            return {"name": name, "price": price, "img": img_url}
    except:
        return None
    return None

# 3. Memory Setup
if 'history' not in st.session_state:
    st.session_state.history = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = "Togedemaru 104"

# 4. Sidebar (Left) - History
with st.sidebar:
    st.title("🕒 Recent")
    for item in reversed(st.session_state.history):
        if st.button(item, key=f"hist_{item}", use_container_width=True):
            st.session_state.search_query = item
            st.rerun()

# 5. Main Layout
main_col, fav_col = st.columns([3, 1], gap="large")

with main_col:
    st.title("🎴 Pokémon Card Price Finder")
    card_name = st.text_input("Search a card", value=st.session_state.search_query)

    if card_name:
        if card_name not in st.session_state.history:
            st.session_state.history.append(card_name)
        
        with st.spinner('Scooping live data...'):
            res = scoop_card_data(card_name)
            if res:
                c1, c2 = st.columns([1, 2])
                with c1:
                    if res['img']: st.image(res['img'], width=250)
                with c2:
                    st.header(res['name'])
                    st.subheader(f"Current Price: {res['price']}")
                
                # Auto-Scroll
                st.components.v1.html(
                    "<script>window.parent.document.querySelector('section.main').scrollTo({top: 1000, behavior: 'smooth'});</script>",
                    height=0
                )
            else:
                st.warning("No results found.")

with fav_col:
    st.markdown("### ⭐ Happyboy457’s favorites")
    
    fav_list = ["Togedemaru 104", "Guzzlord gx sv71", "Scizor GX SV72", "zoroark gx 77a"]
    
    for fav in fav_list:
        data = scoop_card_data(fav)
        if data:
            if data['img']: st.image(data['img'], width=150)
            st.write(f"**{data['name']}**")
            st.write(f"Price: {data['price']}")
            if st.button(f"View Details", key=f"btn_{fav}", use_container_width=True):
                st.session_state.search_query = fav
                st.rerun()
            st.divider()
