import requests
from bs4 import BeautifulSoup

def get_card_data(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # URL construction
    search_url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=prices"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Check for a search results list row
        product_row = soup.find("tr", id=lambda x: x and x.startswith("product-"))
        
        if product_row:
            title_tag = product_row.find("td", class_="title").find("a")
            card_name = title_tag.text.strip()
            card_page_link = "https://www.pricecharting.com" + title_tag['href']
            
            ungraded = product_row.find("td", class_="price numeric used_price")
            psa10 = product_row.find("td", class_="price numeric graded_price")
            
            # Get image from the specific card page
            card_page_res = requests.get(card_page_link, headers=headers, timeout=5)
            card_soup = BeautifulSoup(card_page_res.text, "html.parser")
            cover_div = card_soup.find("div", class_="cover")
            image_url = cover_div.find("img")['src'] if cover_div else ""
            
            return {
                "name": card_name,
                "price": ungraded.text.strip() if ungraded else "N/A",
                "psa10": psa10.text.strip() if psa10 else "N/A",
                "image": image_url
            }, "Success"

        else:
            # Check for direct product page (H1 title)
            title = soup.find("h1", class_="title")
            if not title:
                return None, "Card not found. Try adding the set or number."
            
            img_tag = soup.find("div", class_="cover").find("img")
            ungraded = soup.find("td", id="used_price")
            psa10 = soup.find("td", id="graded_price")
            
            return {
                "name": title.text.strip(),
                "price": ungraded.text.strip() if ungraded else "N/A",
                "psa10": psa10.text.strip() if psa10 else "N/A",
                "image": img_tag['src'] if img_tag else ""
            }, "Success"

    except Exception as e:
        return None, f"Scraper Error: {str(e)}"
