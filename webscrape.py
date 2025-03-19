from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
import logging
import sys
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

def setup_browser():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless=new")
    prefs = {"profile.managed_default_content_settings.images": 2,
             "profile.default_content_setting_values.notifications": 2,
             "profile.default_content_setting_values.popups": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=chrome_options)

def navigate_to_page(driver, url, timeout=5):
    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(EC.url_contains(url))
        logging.info(f"Navigated to: {url}")
    except Exception as e:
        logging.error(f"Failed to navigate to {url}: {e}")
        raise

def enter_text(driver, by_type, locator, text, timeout=5):
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by_type, locator)))
        element.clear()
        element.send_keys(text)
        logging.info(f"Entered '{text}' into {locator}")
    except Exception as e:
        logging.error(f"Failed to enter text into {locator}: {e}")
        raise

def click_element(driver, by_type, locator, timeout=5):
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by_type, locator)))
        element.click()
        logging.info(f"Clicked element: {locator}")
    except Exception as e:
        logging.error(f"Failed to click element {locator}: {e}")
        raise

def select_dropdown(driver, by_type, locator, index, timeout=5):
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
    navigate_to_page(driver, "https://www.expertflyer.com/login.do")
    enter_text(driver, By.NAME, "email", username)
    enter_text(driver, By.NAME, "password", password)
    click_element(driver, By.NAME, "btnLogIn")
    logging.info("Login successful.")

def fill_fare_search_form(driver):
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
        (By.NAME, "passengerType", 0),
        (By.NAME, "currencyCode", 45),
        (By.NAME, "cabin", 0),
    ]
    for by_type, locator, index in dropdown_config:
        select_dropdown(driver, by_type, locator, index)

def submit_search(driver):
    click_element(driver, By.NAME, "btnSearch")
    logging.info("Search submitted successfully.")

def download_results(driver):
    share_results_locator = (By.XPATH, "/html/body/div[1]/div[4]/div[2]/form/span[2]/a")
    logging.info("Waiting for 'Share Results' button...")
    WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable(share_results_locator))
    click_element(driver, *share_results_locator, timeout=0.5)
    logging.info("Clicked 'Share Results' button.")

    download_button_locator = (By.XPATH, "/html/body/div[1]/div[4]/div[2]/div[2]/form/div[3]/input[3]")
    logging.info("Waiting for 'Download as File' button...")
    WebDriverWait(driver, 0.5).until(EC.visibility_of_element_located(download_button_locator))
    WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable(download_button_locator))
    click_element(driver, *download_button_locator, timeout=10)
    logging.info("Clicked 'Download as File' button.")
    time.sleep(2)


def main():
    driver = setup_browser()
    try:
        username = "andrewpan0729@gmail.com"
        password = "apresearch"
        login_to_expertflyer(driver, username, password)
        fill_fare_search_form(driver)
        submit_search(driver)
        download_results(driver)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed.")

if __name__ == "__main__":
    main()