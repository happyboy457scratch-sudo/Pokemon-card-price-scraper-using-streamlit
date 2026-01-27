import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from bs4 import BeautifulSoup

# --- 1. INITIALIZE FIREBASE ---
def init_firebase():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_service_account"])
            fb_creds["private_key"] = fb_creds["private_key"].replace('\\n', '\n').strip()
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase failed to load: {e}")
            st.stop()

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
    except Exception:
        return None

# --- 3. ACCOUNT UI (The Login Gate) ---
if 'user' not in st.session_state:
    st.title("🎴 Pokémon Price Tracker")
    st.subheader("Login or Create an Account to continue")
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        login_email = st.text_input("Email", key="l_email")
        login_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Log In"):
            if login_email:
                try:
                    user = auth.get_user_by_email(login_email)
                    st.session_state.user = user.uid
                    st.session_state.email = login_email
                    st.rerun()
                except Exception:
                    st.error("Login failed. Check your email or create an account.")
            else:
                st.warning("Please enter an email.")

    with tab2:
        new_email = st.text_input("New Email", key="s_email")
        new_pass = st.text_input("New Password", type="password", key="s_pass")
        if st.button("Register Account"):
            if new_email and len(new_pass) >= 6:
                try:
                    user = auth.create_user(email=new_email, password=new_pass)
                    st.success("✅ Account created! You can now use the Login tab.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Password must be at least 6 characters.")
    
    st.stop() # This forces the app to wait for login

# --- 4. THE MAIN APP (Only visible when logged in) ---
st.set_page_config(page_title="PokéTracker", layout="wide")
st.title(
