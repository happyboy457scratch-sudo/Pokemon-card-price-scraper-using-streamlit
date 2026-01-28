import requests
from bs4 import BeautifulSoup
import re

def get_card_data(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # We clean the query to help the search engine
    search_query = query.replace(" ", "+")
    search_url = f"https://www.pricecharting.com/search-products?q={search_query}&type=prices"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # --- STEP 1: CHECK IF WE LANDED DIRECTLY ON A PRODUCT PAGE ---
        # Direct pages have an h1 with class 'title'
        title_tag = soup.find("h1", class_="title")
        if title_tag and "Search Results" not in title_tag.text:
            return parse_product_page(soup)

        # --- STEP 2: SEARCH RESULTS LIST ---
        # If we are here, it means we have a list of cards to choose from
        rows = soup.find_all("tr", id=lambda x: x and x.startswith("product-"))
        
        if not rows:
            return None, "No results found. Try adding the card number (e.g. 'SM192')."

        # Look for the best match in the results
        best_row = None
        for row in rows:
            row_text = row.find("td", class_="title").text.lower()
            # If the user typed 'SM192' and the row contains 'SM192', that's our card
            if query.lower() in row_text or any(word in row_text for word in query.lower().split()):
                best_row = row
                break
        
        if not best_row:
            best_row = rows[0] # Fallback to first result

        # Extract info from the row
        title_link = best_row.find("td", class_="title").find("a")
        card_name = title_link.text.strip()
        card_url = "https://www.pricecharting.com" + title_link['href']
        
        # Prices in the table are under specific classes
        ungraded = best_row.find("td", class_="price numeric used_price")
        psa10 = best_row.find("td", class_="price numeric graded_price")

        # To get the image, we must visit the specific card page
        page_res = requests.get(card_url, headers=headers, timeout=5)
        page_soup = BeautifulSoup(page_res.text, "html.parser")
        img_container = page_soup.find("div", class_="cover")
        image_url = img_container.find("img")['src'] if img_container else ""

        return {
            "name": card_name,
            "price": ungraded.text.strip() if ungraded else "N/A",
            "psa10": psa10.text.strip() if psa10 else "N/A",
            "image": image_url
        }, "Success"

    except Exception as e:
        return None, f"Error: {str(e)}"

def parse_product_page(soup):
    """Helper to parse a single product page if the search goes there directly."""
    title = soup.find("h1", class_="title").text.strip()
    img = soup.find("div", class_="cover").find("img")['src']
    
    # On product pages, prices are in a table with specific IDs
    ungraded = soup.find("td", id="used_price")
    psa10 = soup.find("td", id="graded_price")
    
    return {
        "name": title,
        "price": ungraded.text.strip() if ungraded else "N/A",
        "psa10": psa10.text.strip() if psa10 else "N/A",
        "image": img if img else ""
    }, "Success"
