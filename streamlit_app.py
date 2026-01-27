import streamlit as st
import requests
from bs4 import BeautifulSoup
import statistics

st.set_page_config(page_title="Pocket PriceCharting", page_icon="📈")

st.title("📈 Pocket PriceCharting")
st.write("Real-time market value based on recent eBay sales.")

def get_market_price(card_name):
    # The URL specifically asks eBay for Sold/Completed items
    url = f"https://www.ebay.com/sch/i.html?_nkw={card_name.replace(' ', '+')}+pokemon+card&LH_Sold=1&LH_Complete=1"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tags = soup.find_all('span', {'class': 's-item__price'})
        
        raw_prices = []
        for tag in price_tags:
            # Clean text and handle ranges
            text = tag.text.replace('$', '').replace(',', '').split('to')[0].strip()
            try:
                price = float(text)
                # Ignore items under $0.99 (usually shipping scams or digital cards)
                if price > 0.99:
                    raw_prices.append(price)
            except:
                continue
        
        if len(raw_prices) > 3:
            # PriceCharting Logic: Remove the highest and lowest to get the 'True' average
            raw_prices.sort()
            trimmed_prices = raw_prices[1:-1] 
            return statistics.mean(trimmed_prices), len(raw_prices)
        return None, 0
    except:
        return None, 0

# --- THE UI ---
query = st.text_input("Search for a card:", placeholder="e.g. Umbreon VMAX 215/203")

if query:
    with st.spinner('Calculating market value...'):
        avg, count = get_market_price(query)
        
        if avg:
            st.metric(label="Estimated Market Price", value=f"${avg:.2f}")
            st.caption(f"Based on {count} recent sales found on eBay.")
            
            # Fun PriceCharting style "Conditions"
            col1, col2 = st.columns(2)
            col1.button("Ungraded", use_container_width=True)
            col2.button("PSA 10 (coming soon)", disabled=True, use_container_width=True)
        else:
            st.error("No data found. Try being more specific with the set number!")

st.divider()
st.info("💡 Tip: Add the card number (like '173/151') for much more accurate prices!")
