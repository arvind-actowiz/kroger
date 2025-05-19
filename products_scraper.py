from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from core.driver_setup import get_driver
from core.database import DatabaseManager
from core.config import DB_CONFIG


def extract_price_and_mrp(text):
    if "Sale:" in text:
        parts = text.replace("Sale:", "").replace("discounted from", "").split()
        return parts[0], parts[1]
    else:
        value = text.strip()
        return value, value


def extract_product_details(driver, product_url):
    driver.execute_script(f"window.open('{product_url}', '_blank');")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])

    p_name = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-details-name']").text
    p_upc = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-details-upc']").text.replace("UPC: ", "").strip()
    p_image = driver.find_element(By.CLASS_NAME, "ProductImages-image").get_attribute("src")
    p_store_location = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-details-location']").text.replace("Located in ", "").strip()
    p_size = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-details-item-unit']").text

    raw_price_label = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-item-unit-price']").get_attribute("aria-label")

    p_price, p_mrp = extract_price_and_mrp(raw_price_label)

    product_details = {
        # "itemId": "",
        "UPC": p_upc,
        # "productId": "",
        "URL": product_url,
        "name": p_name,
        "categories": [],
        "image": p_image,
        "storeId": "",
        "storeLocation": p_store_location,
        "price": p_price,
        "mrp": p_mrp,
        # "discount": 0.0,
        "availability": "in stock",
        "keyword": "",
        "size": p_size
    }
    print(product_details)

    driver.close()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    
    return product_details


def scrape_category_products(driver, category_name, category_url):
    """Scrape product details from a category's prodcuts page"""
    try:
        # Open URL in current tab
        driver.get(category_url)
        
        # Load all products till "Load more" button is not available
        while True:
            try:
                load_more_btn = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "LoadMore__load-more-button"))
                )
            except Exception:
                print("Loaded all the products")
                break

            # Scroll to button
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});",
                load_more_btn
            )
            time.sleep(1)
            try:
                load_more_btn.click()
            except ElementClickInterceptedException:
                # Close the dialog by clicking "No, thanks" button
                print("Feedback dialogue appeared, closing it...")
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'No, thanks')]"))
                )
                button.click()
                time.sleep(1)
                load_more_btn.click()
            except StaleElementReferenceException as e:
                load_more_btn = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "LoadMore__load-more-button"))
                )
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});",
                    load_more_btn
                )
                load_more_btn.click()
                time.sleep(1)
        
        products = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )

        print("Total products: ", len(products))

        products_data = []

        for product in products:
            print("Product: ", product.find_element(By.CLASS_NAME, "text-primary").text)
            product_url = product.find_element(By.TAG_NAME, 'a').get_attribute('href')

            product_details = extract_product_details(driver, product_url)
            product_details['categories'] = [category_name]
            products_data.append(product_details)

            # REMOVE ME LATER
            db.insert_products([product_details])
            
        return products_data
    
    finally:
        pass

if __name__ == "__main__":
    driver = get_driver(headless=False)

    with DatabaseManager(DB_CONFIG) as db:
        categories = db.get_pending_categories()
        print(f"Found {len(categories)} categories to process")

        for category in categories:
                print(f"Processing category: {category['category_name']}")
                products = scrape_category_products(driver, category['category_name'], category['category_url'])

                # UNCOMMENT ME LATER
                # db.insert_products(products)
