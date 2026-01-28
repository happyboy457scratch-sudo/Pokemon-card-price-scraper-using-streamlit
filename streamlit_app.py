import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from price_scraper import get_card_data

st.set_page_config(page_title="PokéValue Social", page_icon="🌐", layout="wide")

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_all_data():
    try:
        df = conn.read(ttl="0")
        if df.empty:
            # If the sheet is empty, return a dataframe with the correct headers
            return pd.DataFrame(columns=['trainer', 'owner_email', 'name', 'price', 'image'])
        return df
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return pd.DataFrame(columns=['trainer', 'owner_email', 'name', 'price', 'image'])

def save_to_sheet(new_row):
    existing_df = get_all_data()
    # Clean any empty/NaN columns to prevent concat errors
    new_data = pd.DataFrame([new_row])
    updated_df = pd.concat([existing_df.dropna(how='all', axis=1), new_data], ignore_index=True)
    conn.update(data=updated_df)

# --- AUTH ---
if not st.user.is_logged_in:
    st.title("Trainer Login")
    if st.button("Log in with Auth0"): 
        st.login("auth0")
    st.stop()

# --- THE "BUT THEN" BUG FIXER ---
# This block ensures we don't crash even if the sheet is freshly made
all_data = get_all_data()
user_email = st.user.email

# Verify column existence
if 'owner_email' not in all_data.columns:
    st.error("Sheet Sync Error: Please make sure Row 1 of your sheet has headers: trainer, owner_email, name, price, image")
    st.stop()

# Find the Trainer Handle
user_record = all_data[all_data['owner_email'] == user_email]
trainer_handle = user_record.iloc[0]['trainer'] if not user_record.empty else None

# --- SIDEBAR & PAGES ---
if not trainer_handle:
    st.header("Welcome, New Trainer!")
    new_handle = st.text_input("Choose your Trainer Name (this is permanent):")
    if st.button("Register Account"):
        if new_handle and new_handle not in all_data['trainer'].values:
            save_to_sheet({
                "trainer": new_handle, 
                "owner_email": user_email, 
                "name": "First Card", 
                "price": "$0", 
                "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
            })
            st.success("Account created!")
            st.rerun()
        else:
            st.error("Name taken or empty!")
else:
    st.sidebar.title(f"🎒 {trainer_handle}")
    menu = st.sidebar.radio("Menu", ["Search", "Vault", "Community"])
    
    if menu == "Search":
        # ... [Same Search code as before]
        query = st.text_input("Search for a card:")
        if query:
            data, status = get_card_data(query)
            if data and st.button("Add to Vault"):
                data.update({"trainer": trainer_handle, "owner_email": user_email})
                save_to_sheet(data)
                st.success("Caught it!")
