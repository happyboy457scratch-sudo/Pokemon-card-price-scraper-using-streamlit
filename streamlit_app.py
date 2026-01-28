import streamlit as st
import requests
from price_scraper import get_card_data

# --- 1. PAGE SETUP (New clean emoji) ---
st.set_page_config(page_title="PokéValue", page_icon="📈")

# --- 2. THE LOGIN GATE ---
try:
    if not st.user.is_logged_in:
        st.title("Trainer Login")
        if st.button("Log in with Google"):
            st.login()
        st.stop()
except Exception as e:
    st.error("🔑 Connection Error: Please check your Streamlit 'Secrets' for the Client ID.")
    st.stop()

# --- 3. THE APP ---
ADMIN_EMAIL = "Happyboy457scratch@gmail.com" # Put your email here!
is_admin = (st.user.email == ADMIN_EMAIL)

st.title("Pocket PriceCharting")
st.sidebar.write(f"Logged in as: {st.user.name}")

query = st.text_input("Search for a card:", placeholder="e.g. Charizard 4/102")

if query:
    data, status = get_card_data(query)
    if data:
        col1, col2 = st.columns(2)
        with col1:
            st.image(data['image'])
        with col2:
            st.header(data['name'])
            if data['price']:
                st.metric("Market Price", f"${data['price']:.2f}")
            
            if is_admin:
                st.button("Admin: Save to Collection")
    else:
        st.error(f"Search failed: {status}")

if st.sidebar.button("Logout"):
    st.logout()
