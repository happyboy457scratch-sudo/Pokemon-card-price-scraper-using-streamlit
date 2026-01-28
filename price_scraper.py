import requests
from bs4 import BeautifulSoup

def get_card_data(query):
    # Format the search URL for PriceCharting
    search_query = query.replace(" ", "+")
    search_url = f"https://www.pricecharting.com/search-products?q={search_query}&type=prices"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Find the first product result in the table
        product_row = soup.find("tr", id=lambda x: x and x.startswith("product-"))
        if not product_row:
            return None, "Card not found on PriceCharting."

        # 2. Extract Title and Image
        title_tag = product_row.find("td", class_="title").find("a")
        card_name = title_tag.text.strip()
        # Direct link to the card page to get the image
        card_page_url = "https://www.pricecharting.com" + title_tag['href']
        
        # 3. Get Prices (Ungraded is usually the first price column)
        # PriceCharting uses specific classes for prices
        ungraded_price = product_row.find("td", class_="price numeric used_price")
        psa10_price = product_row.find("td", class_="price numeric graded_price")

        # 4. Fetch the Image from the specific card page
        card_page = requests.get(card_page_url, headers=headers)
        card_soup = BeautifulSoup(card_page.text, "html.parser")
        img_tag = card_soup.find("div", class_="cover").find("img")
        image_url = img_tag['src'] if img_tag else ""

        return {
            "name": card_name,
            "price": ungraded_price.text.strip() if ungraded_price else "N/A",
            "psa10": psa10_price.text.strip() if psa10_price else "N/A",
            "image": image_url
        }, "Success"

    except Exception as e:
        return None, f"PriceCharting Error: {str(e)}"
