import streamlit as st
import requests
from price_scraper import get_card_data

st.set_page_config(page_title="PokéValue Admin", page_icon="📈")

# --- AUTH0 LOGIN ---
# We must pass "auth0" here so it matches your secrets header
if not st.user.is_logged_in:
    st.title("Trainer Login")
    if st.button("Log in with Auth0"):
        st.login("auth0")  # <--- THIS IS THE KEY CHANGE
    st.stop()

# --- ADMIN CHECK ---
ADMIN_EMAIL = "Happyboy457scratch@gmail.com" 
is_admin = (st.user.email == ADMIN_EMAIL)

# --- APP INTERFACE ---
st.title("Pocket PriceCharting")
st.sidebar.write(f"User: {st.user.name}")

query = st.text_input("Search for a card:", placeholder="e.g. Lugia 9/111")

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
