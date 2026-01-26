import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="TCG Price Tracker", page_icon="🎴")

st.title("🎴 Pokémon Card Price Finder")
st.write("Enter the name of a card to see prices and images.")

card_name = st.text_input("Card Name (e.g. Lugia Neo Genesis)", "")

if card_name:
    with st.spinner('Fetching cards and images...'):
        search_url = f"https://www.pricecharting.com/search-products?q={card_name.replace(' ', '+')}&type=prices"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            cards = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))
            
            if not cards:
                st.warning("No cards found. Try being more specific.")
            else:
                for card in cards:
                    # 1. Get the Name
                    name = card.find('td', class_='title').text.strip()
                    
                    # 2. Get the Price
                    price = card.find('td', class_='numeric').text.strip()
                    
                    # 3. Get the Image URL
                    # We look for the 'img' tag and get its 'src' attribute
                    img_tag = card.find('img')
                    img_url = img_tag['src'] if img_tag else None

                    # 4. Display in Columns
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        if img_url:
                            st.image(img_url, width=100)
                    
                    with col2:
                        st.write(f"### {name}")
                    
                    with col3:
                        st.write(f"## {price}")
                    
                    st.divider()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
