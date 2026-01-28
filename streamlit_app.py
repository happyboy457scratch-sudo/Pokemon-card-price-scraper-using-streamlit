import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from price_scraper import get_card_data

st.set_page_config(page_title="PokéValue Social", page_icon="🌐", layout="wide")

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_all_data():
    try:
        # ttl="0" ensures we get the latest data every time we refresh
        return conn.read(ttl="0")
    except:
        # Returns an empty dataframe with our required headers if the sheet is blank
        return pd.DataFrame(columns=['trainer', 'owner_email', 'name', 'price', 'image'])

def save_to_sheet(new_row):
    existing_df = get_all_data()
    # Convert new_row to a DataFrame and join it with existing data
    new_data = pd.DataFrame([new_row])
    updated_df = pd.concat([existing_df, new_data], ignore_index=True)
    conn.update(data=updated_df)

# --- AUTH & USER CHECK ---
if not st.user.is_logged_in:
    st.title("Trainer Login")
    if st.button("Log in with Auth0"): 
        st.login("auth0")
    st.stop()

# --- DATA PROCESSING ---
all_data = get_all_data()
user_email = st.user.email

# Safety check: Get the handle for the current logged-in user
trainer_handle = None
if not all_data.empty and 'owner_email' in all_data.columns:
    user_record = all_data[all_data['owner_email'] == user_email]
    if not user_record.empty:
        trainer_handle = user_record.iloc[0]['trainer']

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🎮 PokéCenter")

if not trainer_handle:
    st.sidebar.warning("Choose your Trainer Name!")
    new_handle = st.sidebar.text_input("Trainer Name:")
    if st.sidebar.button("Register"):
        # Check if name is taken
        is_taken = False
        if not all_data.empty and 'trainer' in all_data.columns:
            if new_handle in all_data['trainer'].values:
                is_taken = True
        
        if new_handle and not is_taken:
            # Create a registration row
            reg_row = {
                "trainer": new_handle, 
                "owner_email": user_email, 
                "name": "SYSTEM_REG", 
                "price": "0", 
                "image": ""
            }
            save_to_sheet(reg_row)
            st.rerun()
        else: 
            st.sidebar.error("Name taken or invalid!")
else:
    st.sidebar.success(f"Trainer: {trainer_handle}")
    menu = st.sidebar.radio("Go to:", ["🔍 Search & Add", "🎒 My Vault", "🌐 Community"])
    if st.sidebar.button("Logout"): 
        st.logout()

# --- APP PAGES ---
if trainer_handle:
    if menu == "🔍 Search & Add":
        st.title("Market Search")
        query = st.text_input("Search for a card (e.g. Pikachu 160/159):")
        if query:
            data, status = get_card_data(query)
            if data:
                c1, c2 = st.columns([1, 2])
                with c1: st.image(data['image'])
                with c2:
                    st.header(data['name'])
                    st.metric("Current Value", data['price'])
                    if st.button("💾 Save to My Vault"):
                        data.update({"trainer": trainer_handle, "owner_email": user_email})
                        save_to_sheet(data)
                        st.success("Card secured in the cloud!")
            else: st.error(status)

    elif menu == "🎒 My Vault":
        st.title(f"🎒 {trainer_handle}'s Collection")
        if not all_data.empty:
            my_cards = all_data[(all_data['trainer'] == trainer_handle) & (all_data['name'] != "SYSTEM_REG")]
            if my_cards.empty:
                st.info("Your vault is empty.")
            else:
                for _, card in my_cards.iterrows():
                    with st.container(border=True):
                        col1, col2 = st.columns([1, 4])
                        col1.image(card['image'], width=100)
                        col2.subheader(card['name'])
                        col2.write(f"**Value:** {card['price']}")

    elif menu == "🌐 Community":
        st.title("🌐 Global Vaults")
        if not all_data.empty:
            other_trainers = all_data[all_data['trainer'] != trainer_handle]['trainer'].unique()
            if len(other_trainers) == 0:
                st.info("No other trainers found yet.")
            else:
                target = st.selectbox("Select a Trainer:", ["Select..."] + list(other_trainers))
                if target != "Select...":
                    their_cards = all_data[(all_data['trainer'] == target) & (all_data['name'] != "SYSTEM_REG")]
                    st.subheader(f"Viewing {target}'s Binder")
                    cols = st.columns(4)
                    for i, (_, card) in enumerate(their_cards.iterrows()):
                        with cols[i % 4]:
                            st.image(card['image'], caption=f"{card['name']} ({card['price']})")
