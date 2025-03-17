from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
import logging
import sys
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

def setup_browser():
    """Initializes and configures the Chrome WebDriver."""
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # Enable for headless mode
    prefs = {"profile.managed_default_content_settings.images": 2}  # Disable images
    chrome_options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=chrome_options)

def navigate_to_page(driver, url, timeout=10):
    """Navigates to the specified URL and waits for the page to load."""
    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(EC.url_contains(url)) #Verify url is correct
        logging.info(f"Navigated to: {url}")
    except Exception as e:
        logging.error(f"Failed to navigate to {url}: {e}")
        raise

def enter_text(driver, by_type, locator, text, timeout=10):
    """Enters text into a specified input field."""
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by_type, locator)))
        element.clear()
        element.send_keys(text)
        logging.info(f"Entered '{text}' into {locator}")
    except Exception as e:
        logging.error(f"Failed to enter text into {locator}: {e}")
        raise

def click_element(driver, by_type, locator, timeout=10):
    """Clicks on a specified element."""
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by_type, locator)))
        element.click()
        logging.info(f"Clicked element: {locator}")
    except Exception as e:
        logging.error(f"Failed to click element {locator}: {e}")
        raise

def select_dropdown(driver, by_type, locator, index, timeout=10):
    """Selects an option from a dropdown menu by index."""
    try:
        select_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by_type, locator)))
        select = Select(select_element)
        selected_option = select.options[index].text
        select.select_by_index(index)
        logging.info(f"Selected '{selected_option}' in {locator}")
    except Exception as e:
        logging.error(f"Failed to select from {locator}: {e}")
        raise

def login_to_expertflyer(driver, username, password):
    """Logs in to ExpertFlyer."""
    navigate_to_page(driver, "https://www.expertflyer.com/login.do")
    enter_text(driver, By.NAME, "email", username)
    enter_text(driver, By.NAME, "password", password)
    click_element(driver, By.NAME, "btnLogIn")
    logging.info("Login successful.")

def fill_fare_search_form(driver):
    """Fills the fare search form."""
    navigate_to_page(driver, "https://www.expertflyer.com/air/fareInformation.do")
    today = date.today().strftime("%m/%d/%Y")
    one_week_later = (date.today() + timedelta(days=7)).strftime("%m/%d/%Y")

    fields = {
        "departingAirport": ("Taipei, Taiwan, Taiwan Taoyuan International Airport (TPE)", By.NAME, "departingAirport"),
        "arrivingAirport": ("San Francisco, CA, USA, San Francisco International Airport (SFO)", By.NAME, "arrivingAirport"),
        "purchasingAirport": ("Taipei, Taiwan, Taiwan Taoyuan International Airport (TPE)", By.NAME, "purchasingAirport"),
        "departDate": (today, By.NAME, "departDate"),
        "returnDate": (one_week_later, By.NAME, "returnDate"),
        "airline": ("China Airlines (CI)", By.NAME, "airline"),
        "fareBasisCode": ("", By.NAME, "fareBasisCode"),
        "ticketingDate": (today, By.NAME, "ticketingDate"),
    }
    for value, by_type, locator in fields.values():
        enter_text(driver, by_type, locator, value)

    dropdown_config = [
        (By.NAME, "passengerType", 0),  # Adult
        (By.NAME, "currencyCode", 45),  # Currency selection
        (By.NAME, "cabin", 0),  # Default cabin
    ]
    for by_type, locator, index in dropdown_config:
        select_dropdown(driver, by_type, locator, index)

def submit_search(driver):
    """Submits the fare search form."""
    click_element(driver, By.NAME, "btnSearch")
    logging.info("Search submitted successfully.")

def main():
    """Main function to execute the script."""
    driver = setup_browser()
    try:
        username = "andrewpan0729@gmail.com"
        password = "apresearch"
        login_to_expertflyer(driver, username, password)
        fill_fare_search_form(driver)
        submit_search(driver)
        time.sleep(1) #Improve this with explicit waits for results
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed.")

if __name__ == "__main__":
    main()