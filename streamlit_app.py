import streamlit as st
import json
import os
from price_scraper import get_card_data

st.set_page_config(page_title="PokéValue Social", page_icon="🎴", layout="wide")

# --- DATABASE SETUP ---
DB_FILE = "collection.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_card(card_data, handle):
    all_data = load_data()
    all_data.append({**card_data, "trainer": handle})
    with open(DB_FILE, "w") as f:
        json.dump(all_data, f, indent=4)

# --- AUTH & USERNAME ---
if not st.user.is_logged_in:
    st.title("Trainer Login")
    if st.button("Log in with Auth0"): st.login("auth0")
    st.stop()

# Initialize Trainer Handle in Session
if "trainer_handle" not in st.session_state:
    st.session_state.trainer_handle = None

# Force username creation if they don't have one
all_cards = load_data()
existing_trainers = list(set([c['trainer'] for c in all_cards]))

# Check if this specific logged-in user already has a handle in the DB
user_id = st.user.email
my_previous_cards = [c for c in all_cards if c.get('owner_email') == user_id]
if my_previous_cards:
    st.session_state.trainer_handle = my_previous_cards[0]['trainer']

# --- SIDEBAR NAV ---
st.sidebar.title("🎮 PokéCenter")
if not st.session_state.trainer_handle:
    st.sidebar.warning("Set your Trainer Name to start!")
    new_handle = st.sidebar.text_input("Choose Trainer Name:")
    if st.sidebar.button("Register Handle"):
        if new_handle and new_handle not in existing_trainers:
            st.session_state.trainer_handle = new_handle
            st.rerun()
        else:
            st.sidebar.error("Name taken or empty!")
else:
    st.sidebar.success(f"Trainer: {st.session_state.trainer_handle}")
    menu = st.sidebar.radio("Go to:", ["🔍 Search & Add", "🎒 My Vault", "🌐 Community Vaults"])
    if st.sidebar.button("Logout"): st.logout()

# --- APP LOGIC ---
if st.session_state.trainer_handle:
    
    # 1. SEARCH & ADD
    if menu == "🔍 Search & Add":
        st.title("Find New Cards")
        query = st.text_input("Enter card name:")
        if query:
            data, status = get_card_data(query)
            if data:
                c1, c2 = st.columns([1, 2])
                with c1: st.image(data['image'])
                with c2:
                    st.header(data['name'])
                    st.metric("Market Price", data['price'])
                    if st.button("➕ Add to My Collection"):
                        # Attach owner_email so we recognize them next time they login
                        data['owner_email'] = st.user.email 
                        save_card(data, st.session_state.trainer_handle)
                        st.success("Added to your vault!")
            else: st.error(status)

    # 2. MY VAULT
    elif menu == "🎒 My Vault":
        st.title(f"🎒 {st.session_state.trainer_handle}'s Vault")
        my_cards = [c for c in all_cards if c['trainer'] == st.session_state.trainer_handle]
        if not my_cards:
            st.info("Your vault is empty! Go catch 'em all.")
        else:
            for idx, card in enumerate(my_cards):
                with st.container(border=True):
                    col1, col2 = st.columns([1, 4])
                    col1.image(card['image'], width=100)
                    col2.subheader(card['name'])
                    col2.write(f"Value: {card['price']}")

    # 3. COMMUNITY VAULTS
    elif menu == "🌐 Community Vaults":
        st.title("🌐 Global Trainer Rankings")
        other_trainers = [t for t in existing_trainers if t != st.session_state.trainer_handle]
        
        if not other_trainers:
            st.info("No other trainers have joined yet. Invite your friends!")
        else:
            target_trainer = st.selectbox("Select a Trainer to view their vault:", ["Choose..."] + other_trainers)
            if target_trainer != "Choose...":
                st.divider()
                st.subheader(f"Viewing {target_trainer}'s Collection")
                their_cards = [c for c in all_cards if c['trainer'] == target_trainer]
                
                # Display in a nice grid
                cols = st.columns(3)
                for i, card in enumerate(their_cards):
                    with cols[i % 3]:
                        st.image(card['image'], caption=f"{card['name']} ({card['price']})")
