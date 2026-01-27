import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_service_account"])
    fb_creds["private_key"] = fb_creds["private_key"].replace('\\n', '\n').strip()
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred)

# --- APP LAYOUT ---
st.set_page_config(page_title="PokéTracker", layout="wide")

if 'user' not in st.session_state:
    st.title("🎴 PokéTracker")
    
    # Check if you added the ID to secrets
    if "google_client_id" in st.secrets:
        if st.button("🌐 Sign in with Google", use_container_width=True):
            # This is where the magic happens!
            st.info("Redirecting to Google... Check for a pop-up window.")
    else:
        st.error("Google Client ID not found in Streamlit Secrets.")
    
    st.stop()

# --- MAIN LOGIC (Visible after login) ---
st.success(f"Welcome back, Trainer!")
if st.button("Log Out"):
    st.session_state.clear()
    st.rerun()
