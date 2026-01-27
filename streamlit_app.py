import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from bs4 import BeautifulSoup

# --- 1. INITIALIZE FIREBASE (The "Safe" Connection) ---
if not firebase_admin._apps:
    try:
        # Pulls the data you saved in the Streamlit Secrets box
        firebase_info = dict(st.secrets["firebase_service_account"])
        # Fixes the formatting for the private key
        firebase_info["private_key"] = firebase_info["private_key"].replace('\\n', '\n')
        
        cred = credentials.Certificate(firebase_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error("Firebase failed to load. Check your Secrets formatting!")
        st.stop()

# --- 2. LIVE INTERNET SCRAPER FUNCTION ---
def scoop_prices(query):
    search_url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
        
        results = []
        for row in rows[:3]: # Gets top 3 matches
            name = row.find('td', class_='title').text.strip()
            price = row.find('td', class_='numeric').text.strip()
            img_tag = row.find('img')
            img_url = img_tag['src'] if img_tag else None
            results.append({"name": name, "price": price, "img": img_url})
        return results
    except Exception as e:
        return None

# --- 3. ACCOUNT UI (Top Right-ish) ---
if 'user' not in st.session_state:
    st.title("🎴 Pokémon Price Tracker")
    st.subheader("Login to see your collection")
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        login_email = st.text_input("Email", key="l_email")
        login_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Log In"):
            # In a real app, you'd verify the password via Firebase Auth REST API
            # For now, we check if the user exists
            try:
                user = auth.get_user_by_email(login_email)
                st.session_state.user = user.uid
                st.session_state.email = login_email
                st.rerun()
            except:
                st.error("Invalid email
