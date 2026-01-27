import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from bs4 import BeautifulSoup

# --- 1. FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"])
        fb_creds["private_key"] = fb_creds["private_key"].replace('\\n', '\n').strip()
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error("Missing Firebase Secrets! Go to Settings > Secrets.")
        st.stop()

# --- 2. LOGIN PAGE ---
if 'user' not in st.session_state:
    st.title("🎴 PokéTracker")
    
    # This checks if you did the Streamlit Settings step correctly
    if "google_client_id" not in st.secrets:
        st.warning("⚠️ **Setup Required:** Go to Streamlit Cloud Settings > Secrets and add your `google_client_id`.")
    
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
                st.error("Invalid email or password.")
        
        st.divider()
        # Google button only lights up if secret is present
        if "google_client_id" in st.secrets:
            if st.button("🌐 Sign in with Google", use_container_width=True):
                st.info("Connecting to Google...")
        else:
            st.button("🌐 Google Auth (Waiting for Secret)", disabled=True, use_container_width=True)

    with tab2:
        new_email = st.text_input("New Email")
        new_pw = st.text_input("New Password", type="password")
        if st.button("Create Account", use_container_width=True):
            try:
                auth.create_user(email=new_email, password=new_pw)
                st.success("Account created! Switch to Login tab.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.stop()

# --- 3. THE SCRAPER (Main App) ---
st.set_page_config(page_title="PokéTracker", layout="wide")
st.title(f"🔍 Welcome, {st.session_state.email}")

def get_card_prices(name):
    url = f"https://www.pricecharting.com/search-products?q={name.replace(' ', '+')}&type=prices"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
        
        results = []
        for r in rows[:3]:
            title = r.find('td', class_='title').text.strip()
            price = r.find('td', class_='numeric').text.strip()
            img = r.find('img')['src'] if r.find('img') else None
            results.append({"name": title, "price": price, "img": img})
        return results
    except:
        return None

search = st.text_input("Search for a Pokémon card:", placeholder="e.g. Mewtwo Base Set")
if search:
    cards = get_card_prices(search)
    if cards:
        for c in cards:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                with col1:
                    if c['img']: st.image(c['img'])
                with col2:
                    st.subheader(c['name'])
                    st.write(f"### Market Price: {c['price']}")
    else:
        st.info("No cards found.")

with st.sidebar:
    if st.button("Log Out"):
        st.session_state.clear()
        st.rerun()
