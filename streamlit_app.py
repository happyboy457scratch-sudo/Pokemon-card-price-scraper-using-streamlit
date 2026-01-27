import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- 1. FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"])
        fb_creds["private_key"] = fb_creds["private_key"].replace('\\n', '\n').strip()
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase Config Error: {e}")
        st.stop()

# --- 2. GOOGLE LOGIN LOGIC ---
# This part checks the URL to see if Google just sent the user back
query_params = st.query_params
if "access_token" in query_params or "id_token" in query_params:
    # If a token is found, we "log in" the user in the session
    st.session_state.user = "google_user"
    st.session_state.email = "Google User" # In a real app, you'd decode the token for the real email

# Build the Google Login URL
params = {
    "client_id": st.secrets["google_client_id"],
    "redirect_uri": "https://tcgpricechecking.streamlit.app",
    "response_type": "token",
    "scope": "openid email profile",
}
google_login_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

# --- 3. LOGIN PAGE UI ---
if 'user' not in st.session_state:
    st.title("🎴 PokéTracker")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            try:
                user = auth.get_user_by_email(email)
                st.session_state.user = user.uid
                st.session_state.email = email
                st.rerun()
            except:
                st.error("Login failed.")
        
        st.divider()
        # REAL WORKING LINK BUTTON
        st.link_button("🌐 Sign in with Google", google_login_url, use_container_width=True)

    with tab2:
        new_email = st.text_input("New Email")
        new_pw = st.text_input("New Password", type="password")
        if st.button("Create Account", use_container_width=True):
            try:
                auth.create_user(email=new_email, password=new_pw)
                st.success("Account created! Go to Login tab.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.stop()

# --- 4. MAIN APP (Price Scraper) ---
st.set_page_config(page_title="PokéTracker", layout="wide")
st.title(f"🔍 Welcome, {st.session_state.email}!")

def get_prices(name):
    url = f"https://www.pricecharting.com/search-products?q={name.replace(' ', '+')}&type=prices"
    # Make sure this line below ends with '})
    headers = {'User-Agent': 'Mozilla/5.0'} 
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
        results = []
        for r in rows[:3]:
            title = r.find('td', class_='title').text.strip()
            price = r.find('td', class_='numeric').text.strip()
            img = r.find('img')['src'] if r.find('img') else None
            results.append({"name": title, "price": price, "img": img})
        return results
    except Exception as e:
        return None
