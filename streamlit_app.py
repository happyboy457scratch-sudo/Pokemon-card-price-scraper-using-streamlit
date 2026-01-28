import streamlit as st
import json
import os
from price_scraper import get_card_data

# --- CONFIG ---
st.set_page_config(page_title="PokéValue Vault", page_icon="📈", layout="wide")

# --- AUTH0 LOGIN ---
if not st.user.is_logged_in:
    st.title("Trainer Login")
    if st.button("Log in with Auth0"):
        st.login("auth0")
    st.stop()

# --- ADMIN SETUP ---
# Update this to your email to regain "Admin" control later
ADMIN_EMAIL = "your-email@gmail.com" 
is_admin = (st.user.email == ADMIN_EMAIL)

# --- COLLECTION DATABASE LOGIC ---
DB_FILE = "collection.json"

def save_to_vault(card_data, user):
    collection = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                collection = json.load(f)
            except:
                collection = []
    
    card_entry = card_data.copy()
    card_entry["owner"] = user
    collection.append(card_entry)
    
    with open(DB_FILE, "w") as f:
        json.dump(collection, f, indent=4)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title(f"Welcome, {st.user.name.split()[0]}!")
# This line helps you debug:
st.sidebar.write(f"Logged in as: {st.user.email}")

menu = st.sidebar.radio("Navigation", ["🔍 Search Market", "🛡️ My Vault"])

if st.sidebar.button("Logout"):
    st.logout()

# --- SEARCH PAGE ---
if menu == "🔍 Search Market":
    st.title("Pocket PriceCharting")
    query = st.text_input("Search for a card:", placeholder="e.g. Lugia #9")

    if query:
        data, status = get_card_data(query)
        
        if data:
            col1, col2 = st.columns([1, 2])
            with col1:
                if data.get('image'):
                    st.image(data['image'], use_container_width=True)
                
            with col2:
                st.header(data['name'])
                p_raw = data.get('price', 'N/A')
                p_psa = data.get('psa10', 'N/A')

                m1, m2 = st.columns(2)
                m1.metric("Ungraded / Raw", p_raw)
                m2.metric("PSA 10 (Graded)", p_psa)

                st.divider()
                # REMOVED the 'if is_admin' check so you can see the button now!
                if st.button("💾 Save to Collection"):
                    save_to_vault(data, st.user.name)
                    st.success(f"Saved {data['name']} to your vault!")
        else:
            st.error(status)

# --- VAULT PAGE ---
else:
    st.title("🛡️ The Collector's Vault")
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                my_cards = json.load(f)
            except:
                my_cards = []
        
        if not my_cards:
            st.info("Your vault is empty.")
        else:
            for idx, card in enumerate(my_cards):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 3, 1])
                    c1.image(card.get('image', ''), width=100)
                    c2.subheader(card.get('name', 'Unknown Card'))
                    c2.write(f"**Raw:** {card.get('price', 'N/A')} | **PSA 10:** {card.get('psa10', 'N/A')}")
                    if c3.button("🗑️", key=f"del_{idx}"):
                        my_cards.pop(idx)
                        with open(DB_FILE, "w") as f:
                            json.dump(my_cards, f, indent=4)
                        st.rerun()
    else:
        st.info("No collection found yet.")
