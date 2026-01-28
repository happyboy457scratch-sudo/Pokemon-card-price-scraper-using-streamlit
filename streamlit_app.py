import streamlit as st
import requests

st.set_page_config(page_title="PokéValue Admin", page_icon="🃏")

# 1. THE GATEKEEPER
# Streamlit's built-in Google login stores user info in st.experimental_user
if not st.experimental_user.is_logged_in:
    st.title("Please Log In")
    st.write("Log in with Google to access the market prices.")
    if st.button("Log in with Google"):
        st.login()
    st.stop()

# 2. DEFINE THE ADMIN
# Put YOUR Gmail address here
ADMIN_EMAIL = "your-email@gmail.com" 
is_admin = st.experimental_user.email == ADMIN_EMAIL

# 3. THE APP
st.title("🃏 Pokémon Card Live Search")

if is_admin:
    st.success(f"Welcome, Admin ({st.experimental_user.name})")
else:
    st.info(f"Welcome, {st.experimental_user.name}")

query = st.text_input("Enter Card Name:", placeholder="e.g. Mewtwo 151/165")

if query:
    with st.spinner("Searching..."):
        try:
            # API Call
            res = requests.get(f"https://api.tcgdex.net/v2/en/cards?name={query}").json()
            if res:
                card = requests.get(f"https://api.tcgdex.net/v2/en/cards/{res[0]['id']}").json()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.image(f"{card.get('image')}/high.webp")
                with col2:
                    st.header(card.get('name'))
                    # Price logic
                    pricing = card.get('pricing', {}).get('tcgplayer', {})
                    price = pricing.get('normal', {}).get('market') or pricing.get('holofoil', {}).get('market')
                    
                    if price:
                        st.metric("Market Price", f"${price:.2f}")
                    else:
                        st.warning("No price data found.")

                    # ADMIN ONLY BUTTON
                    if is_admin:
                        st.divider()
                        if st.button("📝 Edit Database Entry"):
                            st.write("Admin tool: Change card details (Coming Soon)")
            else:
                st.error("Card not found!")
        except:
            st.error("Connection error.")

# Logout button in sidebar
if st.sidebar.button("Logout"):
    st.logout()
