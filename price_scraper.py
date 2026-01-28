import requests
from bs4 import BeautifulSoup

def get_card_data(query):
    # Standard headers to look like a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 1. CLEAN SEARCH
    search_url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=prices"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # 2. FIND THE FIRST PRODUCT
        # PriceCharting results are usually in a table with id 'price_guide'
        product_row = soup.find("tr", id=lambda x: x and x.startswith("product-"))
        
        if not product_row:
            # If we are already on a product page (happens if search is perfect)
            title = soup.find("h1", class_="title")
            if not title:
                return None, "Card not found. Try adding the set name."
            
            card_name = title.text.strip()
            # Grabbing price from the product page table
            ungraded = soup.find("td", id="used_price")
            psa10 = soup.find("td", id="graded_price")
            img_tag = soup.find("div", class_="cover").find("img")
            image_url = img_tag['src'] if img_tag else ""
        else:
            # We are on a search results page
            title_tag = product_row.find("td", class_="title").find("a")
            card_name = title_tag.text.strip()
            
            # Use relative links correctly
            card_page_link = title_tag['href']
            if not card_page_link.startswith("http"):
                card_page_link = "https://www.pricecharting.com" + card_page_link
            
            # Scrape Ungraded and PSA 10 from the search table row
            ungraded_tag = product_row.find("td", class_="price numeric used_price")
            psa10_tag = product_row.find("td", class_="price numeric graded_price")
            
            ungraded = ungraded_tag.text.strip() if ungraded_tag else "N/A"
            psa10 = psa10_tag.text.strip() if psa10_tag else "N/A"
            
            # Quickly grab image from the actual card page
            card_page_res = requests.get(card_page_link, headers=headers, timeout=5)
            card_soup = BeautifulSoup(card_page_res.text, "html.parser")
            cover_div = card_soup.find("div", class_="cover")
            image_url = cover_div.find("img")['src'] if cover_div else ""

        return {
            "name": card_name,
            "price": ungraded if ungraded else "N/A",
            "psa10": psa10 if psa10 else "N/A",
            "image": image_url
        }, "Success"

    except Exception as e:
        return None, f"Scraper Error: {str(e)}"
