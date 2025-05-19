from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from core.database import DatabaseManager
from core.config import DB_CONFIG
from core.driver_setup import get_driver

def click_shop_then_grocery_btn(driver):
    """
    Clicks on Shop > Grocery buttons sequentially when called.
    """
    shop_ctgry_btn = driver.find_element(By.ID, "ExposedMenu-Category-Shop")
    shop_ctgry_btn.click()
    
    # let the panel expand
    time.sleep(1)

    grocery_tab_btn = driver.find_element(By.CSS_SELECTOR, '[data-testid="ExposedMenuTextLink-Grocery"]')
    grocery_tab_btn.click()

    # let the section load
    time.sleep(1)


def scrape_categories(driver, page_url):
    """Scrape category names and URLs from Kroger's homepage"""
    try:
        # Open URL in current tab
        driver.get(page_url)

        wait = WebDriverWait(driver, 10)  # 10 second timeout

        click_shop_then_grocery_btn(driver)

        # get all the categories available
        ctgry_display_section = driver.find_elements(By.CLASS_NAME, "SecondCategoryDisplayer")[1]
        categories_btn_eles = ctgry_display_section.find_elements(By.TAG_NAME, "li")

        flag_to_click = False

        categories_data = []

        # iterate all categories
        for ctgry_btn_ele in categories_btn_eles:
            print("Clicking category: ", ctgry_btn_ele.text)
            
            if flag_to_click:
                ctgry_btn_ele.click()
            else:
                flag_to_click = True
            time.sleep(1)
            
            menu_container = driver.find_element(By.CSS_SELECTOR, '[data-testid="MenuContent-ContentDisplayer"]')
            
            # get all grouped elements
            grouped_eles = menu_container.find_elements(By.TAG_NAME, "ul")

            # iterate grouped eles
            for group_ele in grouped_eles:
                # get all the subcategories
                subcategories = group_ele.find_elements(By.TAG_NAME, "a")

                # iterate subcategories
                for subcat in subcategories:
                    if "shop all" in subcat.text.lower():
                        continue
                    print("Subcategory name: ", subcat.text)
                    print("Subcategory link: ", subcat.get_attribute("href"))

                    categories_data.append({
                        "name": subcat.text,
                        "url": subcat.get_attribute("href")
                    })
        
        return categories_data

    finally:
        pass


if __name__ == "__main__":
    homepage_url = "https://www.kroger.com"

    driver = get_driver(headless=False)

    with DatabaseManager(DB_CONFIG) as db:
        categories = scrape_categories(driver, homepage_url)

        db.insert_categories(categories)

        print("Total categories scraped: ", len(categories))