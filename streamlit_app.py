import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("Pokémon Card Price Tracker")

card_query = st.text_input("Enter Card Name (e.g., Charizard Base Set)", "Pikachu")

if st.button("Search Prices"):
    url = f"https://www.pricecharting.com/search-products?q={card_query.replace(' ', '+')}&type=prices"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    cards = soup.find_all('tr', id=lambda x: x and x.startswith('product-'))

    for card in cards:
        name = card.find('td', class_='title').text.strip()
        price = card.find('td', class_='numeric').text.strip()
        st.write(f"**{name}**: {price}")
