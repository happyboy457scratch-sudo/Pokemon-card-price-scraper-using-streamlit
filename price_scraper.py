import streamlit as st
from price_scraper import get_card_data

st.set_page_config(page_title="PokéValue", page_icon="📈")

# --- AUTH0 LOGIN ---
if not st.user.is_logged_in:
    st.title("Trainer Login")
    if st.button("Log in with Auth0"):
        st.login("auth0")
    st.stop()

# --- ADMIN SETUP ---
# Update this to your actual email address
ADMIN_EMAIL = "your-email@gmail.com" 
is_admin = (st.user.email == ADMIN_EMAIL)

st.title("Pocket PriceCharting")
st.sidebar.write(f"Logged in as: {st.user.name}")

# --- SEARCH UI ---
query = st.text_input("Search for a card:", placeholder="e.g. Lugia #9")

if query:
    data, status = get_card_data(query)
    
    if data:
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            if data.get('image'):
                st.image(data['image'], use_container_width=True)
            
        with col2:
            st.header(data['name'])
            
            # --- THE FIX: NO MORE MATH ERRORS ---
            # We display the price string exactly as it comes from the scraper.
            # No ':.2f' means no more ValueError.
            p_raw = data.get('price', 'N/A')
            p_psa = data.get('psa10', 'N/A')

            m1, m2 = st.columns(2)
            m1.metric("Ungraded / Raw", p_raw)
            m2.metric("PSA 10 (Graded)", p_psa)

            if is_admin:
                st.divider()
                st.button("💾 Save to Collection")
    else:
        st.error(status)

if st.sidebar.button("Logout"):
    st.logout()
