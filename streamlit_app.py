import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from bs4 import BeautifulSoup

# --- 1. INITIALIZE FIREBASE ---
def init_firebase():
    if not firebase_admin._apps:
        try:
            # Pulls from Streamlit Secrets
            fb_creds = dict(st.secrets["firebase_service_account"])
            # Fixes the private key formatting and removes whitespace
            fb_creds["private_key"] = fb_creds["private_key"].replace('\\n', '\n').strip()
            
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase failed to load: {e}")
            st.stop()

# Run the initialization immediately
init_firebase()

# --- 2. LIVE INTERNET SCRAPER ---
def scoop_prices(query):
    search_url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=prices"
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
    except Exception as e:
        return None

# --- 3. ACCOUNT UI (The Login Gate) ---
if 'user' not in st.session_state:
    st.title("🎴 Pokémon Price Tracker")
    st.subheader("Login to see your collection")
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        login_email = st.text_input("Email", key="l_email")
        login_pass = st.text_input("Password", type="password
