import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from bs4 import BeautifulSoup
import os

# --- 1. FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    try:
        # Pulls from the Streamlit Secrets vault you just filled
        fb_secrets = dict(st.secrets["firebase_service_account"])
        # Fixes the private key formatting
        fb_secrets["private_key"] = fb_secrets["private_key"].replace('\\n', '\n')
        
        cred = credentials.Certificate(fb_secrets)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase failed to load. Check your Secrets formatting! Error: {e}")
        st.stop()

# --- 2. SCRAPER FUNCTION ---
def scoop_multiple_cards(card_query):
    search_url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
        results = []
        for row in rows[:3]:
            name = row.find('td', class_='title').text.strip()
            price = row.find('td', class_='numeric').text.strip()
            img_tag = row.find('img')
            img_url = img_tag['src'] if img_tag else None
            results.append({"name": name, "price": price, "img": img_url})
        return results
    except:
        return None

# --- 3. LOGIN / SIGNUP UI ---
st.sidebar.title("🔐 Account")

if 'user' not in st.session_state:
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In"):
            try:
                # In Firebase Admin, we verify the user exists
                user = auth.get_user_by_email(email)
                st.session_state.user = user.uid
                st.session_state.user_email = email
                st.success("Logged in!")
                st.rerun()
            except:
                st.error("User not found. Did you create an account first?")

    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            try:
                user = auth.create_user(email=new_email, password=new_password)
                st.success("Account created! Now go to the Login tab.")
            except Exception as e:
