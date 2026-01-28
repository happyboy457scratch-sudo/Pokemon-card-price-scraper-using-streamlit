import streamlit as st
import requests
from price_scraper import get_card_data

# --- PAGE CONFIG ---
st.set_page_config(page_title="PokéValue", page_icon="📈")

# --- AUTHENTICATION ---
# This uses Streamlit's native Google Auth
if not st.user.is_logged_in:
    st.title("Trainer Login")
    st.info("Log in with Google to access the collection.")
    if st.button("Log in with Google"):
        st.login()
    st.stop()

# --- ADMIN CHECK ---
# Replace with your actual gmail address
ADMIN_EMAIL = "Happyboy457scratch@gmail.com" 
is_admin = (st.user.email == ADMIN_EMAIL)

# --- SEARCH UI ---
st.title("Pocket PriceCharting")
st.sidebar.write(f"Logged in as: {st.user.name}")

query = st.text_input("Search for a card:", placeholder="e.g. Rayquaza VMAX 218/203")

if query:
    with st.spinner("Scanning database..."):
        data, status = get_card_data(query)
        if data:
            col1, col2 = st.columns(2)
            with col1:
                st.image(data['image'])
            with col2:
                st.header(data['name'])
                st.caption(f"Set: {data['set']}")
                if data['price']:
                    st.metric("Market Price", f"${data['price']:.2f}")
                
                # Admin-only buttons
                if is_admin:
                    st.divider()
                    st.button("➕ Add to My Collection")
        else:
            st.error(f"Search failed: {status}")

if st.sidebar.button("Logout"):
    st.logout()
