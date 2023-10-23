from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
import json

ROLE_PROMPT = """You are an experienced retail assistant at Amazon, dedicated to providing top-notch service to our customers. Your mission is to assist customers in finding and purchasing the perfect products that match their needs and preferences. When a customer seeks product recommendations, you can leverage function calls to access our extensive product database and suggest the most suitable items.
Here are the rules:
1. Before making a function call to get products, you should generate a query that fetches products relevant to the user's requirements.
2. You must clarify the user's requirements before making the function call to get products. Understand what they are looking for, their preferences, and any specific criteria they have in mind.
3. Once you have a clear understanding of the user's needs, you can proceed to make the function call.
If you need additional details to make a precise recommendation, feel free to ask the customer pertinent questions."
"""

AMAZON_URL = "https://www.amazon.in/"

def get_clean_price(price):
    try:
        price = float(price.replace('MRP', '').replace('Rs.', '').replace(
            ',', '').replace('₹', '').replace('€', '').replace('$', '').strip())
    except:
        price = None

    return price

def get_product_details(page):
    # fetch price 
    price = page.find('span', {'class': 'a-price-whole'})
    if price is not None:
        price = get_clean_price(price=price.text)
    
    # fetch title
    title = page.find('span', {'id': 'productTitle'})
    if title is not None:
        title = title.text.strip()
    
    # fetch mrp
    mrp_block = page.find(
        'span', {'class': 'a-size-small a-color-secondary aok-align-center basisPrice'})
    mrp = None
    if mrp_block is not None:
        mrp = mrp_block.find('span', {'class': 'a-price a-text-price'}).find(
            'span', {'class': 'a-offscreen'})
        if mrp is not None:
            mrp = get_clean_price(price=mrp.text)
        else:
            mrp = price
    else:
        mrp = price

    # fetch availability
    avalability_block = page.find('div', {'id': 'availability'})
    availability = None
    if avalability_block is not None:
        if avalability_block.find('span', {'class': 'a-color-success'}):
            availability = 'In Stock'
        else:
            availability = 'Out of Stock'
    else:
        availability = 'Out of Stock'

    # fetch rating 
    rating_block = page.find('div', {'id': 'averageCustomerReviews'})
    if rating_block is not None:
        rating = rating_block.find('span', {'class': 'a-icon-alt'})
        if rating:
            rating = float(rating.text.replace(
                ',', '').strip().split(' ')[0])
    else:
        rating = float(0)

    # fetch rating count
    rating_count = page.find('span', {'id': 'acrCustomerReviewText'})
    if rating_count is not None:
        rating_count = float(rating_count.text.replace(
            ',', '').strip().split(' ')[0])
    else:
        rating_count = float(0)

    # fetch product reviews
    reviews = []
    reviews_div = page.find('div', {'id' : 'cm-cr-dp-review-list'})
    if reviews_div:
        review_divs = reviews_div.find_all('div', {'data-hook': 'review'})
        for review_div in review_divs:
            # Extract the review title
            review_title = review_div.find('a', {'data-hook': 'review-title'}).find_all('span')[2].get_text().strip()

            # Extract the review rating
            review_rating = review_div.find('i', {'data-hook': 'review-star-rating'}).find('span', {'class': 'a-icon-alt'}).get_text().strip()

            # Extract the review text
            review_text = review_div.find('span', {'data-hook': 'review-body'}).get_text().strip()

            review = {
                'title' : review_title,
                'review_rating': review_rating,
                'review': review_text
            }
            reviews.append(review)

            # we only need at most 2 reviews per product
            if len(reviews) > 1:
                break

    product = {
        'title': title,
        'price': price,
        'MRP': mrp,
        'availability': availability,
        'rating': rating,
        'rating_count': rating_count,
        'product_link': "",
        'Reviews' : reviews
    }
    return product

def valid(product):
    return False if product['title'] is None or product['price'] is None or product['availability'] == "Out of Stock" else True

async def scrape_products(query):
    print(f"To scrape : {query}\n")
    products = []
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch()
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
            )
            page = await context.new_page()
        except Exception as e:
            print(f'Error while initiating browser instance : {e}')
        
        # we don't want to load images
        await page.route(
            "**/*", 
            lambda route: route.abort() if route.request.resource_type == "image" else route.continue_()
        )

        # navigate to amazon.in 
        await page.goto(AMAZON_URL)

        # wait for search input to be loaded
        await page.wait_for_selector(selector="#twotabsearchtextbox")
        await page.locator("#twotabsearchtextbox").fill(query)

        # wait for submit button to be loaded
        await page.wait_for_selector("#nav-search-submit-button")
        await page.locator("#nav-search-submit-button").click()
        
        # on the products page wait for page to be loaded
        await page.wait_for_load_state("load")
        
        # get the product asins
        asin_divs = await page.query_selector_all("div[data-asin]")
        asins = set()
        if asin_divs:
            for asin_div in asin_divs:
                asin = await asin_div.get_attribute("data-asin")
                if len(asin) == 10:
                    asins.add(asin)
        else:
            print('No products found')
        
        # iterate over available products and fetch their details
        for asin in asins:
            product_url = AMAZON_URL + f'dp/{asin}/'
            
            print(product_url)
            await page.goto(product_url)
            await page.wait_for_load_state('load')

            await page.screenshot(path=f"img/{asin}.png")
            # product details to be fetched : title, price, mrp, availability, rating, rating count, reviews
            
            soup = BeautifulSoup(await page.content(), 'html.parser')
            product = get_product_details(soup)

            if valid(product):
                product['product_link'] = product_url
                products.append(product)

            if len(products) > 2:
                break

    return products

if __name__ == "__main__":
    # for testing purpose
    products = asyncio.run(scrape_products("peanut butter high protein"))
    print(json.dumps(products, indent=4))