import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from bs4 import BeautifulSoup

# --- 1. INITIALIZE FIREBASE ---
if not firebase_admin._apps:
    try:
        firebase_info = dict(st.secrets["firebase_service_account"])
        firebase_info["private_key"] = firebase_info["private_key"].replace('\\n', '\n')
        cred = credentials.Certificate(firebase_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error("Firebase failed to load. Check your Secrets formatting!")
        st.stop()

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

# --- 3. ACCOUNT UI ---
if 'user' not in st.session_state:
    st.title("🎴 Pokémon Price Tracker")
    st.subheader("Login to see your collection")
    
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
                except Exception as e:
                    st.error("Invalid email or user does not exist.")
            else:
                st.warning("Please enter an email address.")

    with tab2:
        new_email = st.text_input("New Email", key="s_email")
        new_pass = st.text_input("New Password", type="password", key="s_pass")
        if st.button("Register Account"):
            try:
                user = auth.create_user(email=new_email, password=new_pass)
                st.success("Account created! Now go to the Login tab.")
            except Exception as e:
                st.error(f"Error creating account: {e}")
    st.stop()

# --- 4. THE MAIN APP (Only shows after Login) ---
st.title(f"Welcome back, {st.session_state.email}!")

col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("🔍 Search any card on the internet:", placeholder="e.g. Umbreon VMAX 215")
