import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from bs4 import BeautifulSoup

# --- 1. FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"])
        fb_creds["private_key"] = fb_creds["private_key"].replace('\\n', '\n').strip()
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase Config Error: {e}")
        st.stop()

# --- 2. THE LOGIN GATE ---
if 'user' not in st.session_state:
    st.title("🎴 PokéTracker")
    st.subheader("Login to access live card prices")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", placeholder="trainer@oak.com")
        pw = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            try:
                user = auth.get_user_by_email(email)
                st.session_state.user = user.uid
                st.session_state.email = email
                st.rerun()
            except:
                st.error("Trainer not found. Check your credentials.")
        
        st.divider()
        if "google_client_id" in st.secrets:
            if st.button("🌐 Sign in with Google", use_container_width=True):
                # Note: This is a placeholder for the OAuth redirect logic
                st.info("Directing to Google Sign-In...")
        else:
            st.button("🌐 Google Auth (Secret Missing)", disabled=True, use_container_width=True)

    with tab2:
        new_email = st.text_input("New Email", key="reg_email")
        new_pw = st.text_input("New Password", type="password", key="reg_pw")
        if st.button("Create Account", use_container_width=True):
            try:
                auth.create_user(email=new_email, password=new_pw)
                st.success("Account created! Switch to the Login tab.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.stop()

# --- 3. MAIN DASHBOARD (Accessible after login) ---
st.set_page_config(page_title="PokéTracker", layout="wide", page_icon="🔍")

# Sidebar
with st.sidebar:
    st.success(f"Logged in: {st.session_state.email}")
    if st.button("Sign Out"):
        st.session_state.clear()
        st.rerun()
    st.divider()
    st.caption("Data provided by PriceCharting")

st.title("🔍 PokéTracker: Live Price Search")

# Scraper Logic
def scoop_prices(query):
    search_url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
        results = []
        for row in rows[:5]: # Showing top 5 results
            name_el = row.find('td', class_='title')
            price_el = row.find('td', class_='numeric')
            if name_el and price_el:
                img_tag = row.find('img')
                results.append({
                    "name": name_el.text.strip(),
                    "price": price_el.text.strip(),
                    "img": img_tag['src'] if img_tag else None
                })
        return results
    except:
        return None

# Search Interface
search_query = st.text_input("Search for a card:", placeholder="e.g., Lugia V Alt Art")

if search_query:
    with st.spinner("Searching the tall grass..."):
        cards = scoop_prices(search_query)
        if cards:
            for c in cards:
                with st.container(border=True):
                    col_img, col_info = st.columns([1, 4])
                    with col_img:
                        if c['img']: st.image(c['img'], width=100)
                    with col_info:
                        st.subheader(c['name'])
                        st.write(f"### {c['price']}")
        else:
            st.info("No cards found. Make sure the name is spelled correctly!")
