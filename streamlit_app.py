import streamlit as st
import requests
from price_scraper import get_card_data

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="PokéValue Admin", page_icon="🃏", layout="centered")

# --- 2. GOOGLE AUTHENTICATION ---
# This uses the secrets you added to your Streamlit dashboard
if not st.user.is_logged_in:
    st.title("🃏 PokéValue Login")
    st.info("Log in with Google to access the live market database.")
    if st.button("Log in with Google"):
        st.login()
    st.stop()

# --- 3. ADMIN CONFIG ---
# Replace with your actual email to unlock admin buttons
ADMIN_EMAIL = "Happyboy457scratch@gmail.com" 
is_admin = (st.user.email == ADMIN_EMAIL)

# --- 4. APP INTERFACE ---
st.title("📈 Pocket PriceCharting")

# Sidebar for logout and status
with st.sidebar:
    st.write(f"Logged in as: **{st.user.name}**")
    if is_admin:
        st.success("Admin Access Granted")
    if st.button("Log out"):
        st.logout()

# Search Input
query = st.text_input("Search for a card:", placeholder="e.g. Umbreon VMAX 215/203")

if query:
    with st.spinner("Fetching live data..."):
        # This calls your price_scraper.py script
        data, status = get_card_data(query)

        if data:
            col1, col2 = st.columns([1, 1.2])

            with col1:
                st.image(data['image'], use_container_width=True)

            with col2:
                st.header(data['name'])
                st.caption(f"Set: {data['set']}")
                
                if data['price']:
                    st.metric("Market Price", f"${data['price']:.2f}")
                    st.success("Live TCGplayer data synced.")
                else:
                    st.warning("Price not available for this specific printing.")

                # Admin-Only Section
                if is_admin:
                    st.divider()
                    st.subheader("Admin Tools")
                    if st.button("➕ Add to My Collection"):
                        st.write("Added! (Logic for saving coming soon)")
                    if st.button("🔍 View eBay Listings"):
                        # This opens a new tab with the eBay "Sold" search
                        ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}+pokemon+card&LH_Sold=1&LH_Complete=1"
                        st.link_button("Go to eBay Sold", ebay_url)
        else:
            st.error(f"Error: {status}")

st.divider()
st.caption("Powered by TCGdex & Streamlit Auth. Safe & Secure.")
