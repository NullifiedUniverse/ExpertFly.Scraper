from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime, timedelta
import logging
import sys
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

def setup_browser():
    chrome_options = webdriver.ChromeOptions()
    # Performance optimizations
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Don't load images
        "profile.default_content_setting_values.notifications": 2,  # Block notifications
        "profile.default_content_setting_values.popups": 2,  # Block popups
        "download.prompt_for_download": False  # Download without prompting
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    return webdriver.Chrome(options=chrome_options)

def navigate_to_page(driver, url, timeout=10):
    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(EC.url_contains(url))
        logging.info(f"Navigated to: {url}")
    except Exception as e:
        logging.error(f"Failed to navigate to {url}: {e}")
        raise

def enter_text(driver, by_type, locator, text, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by_type, locator)))
        element.clear()
        element.send_keys(text)
        logging.info(f"Entered '{text}' into {locator}")
    except Exception as e:
        logging.error(f"Failed to enter text into {locator}: {e}")
        raise

def click_element(driver, by_type, locator, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by_type, locator)))
        element.click()
        logging.info(f"Clicked element: {locator}")
    except Exception as e:
        logging.error(f"Failed to click element {locator}: {e}")
        raise

def select_dropdown(driver, by_type, locator, index, timeout=10):
    try:
        select_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by_type, locator)))
        select = Select(select_element)
        select.select_by_index(index)
        logging.info(f"Selected option index {index} in {locator}")
    except Exception as e:
        logging.error(f"Failed to select from {locator}: {e}")
        raise

def login_to_expertflyer(driver, username, password):
    navigate_to_page(driver, "https://www.expertflyer.com/login.do")
    enter_text(driver, By.NAME, "email", username)
    enter_text(driver, By.NAME, "password", password)
    click_element(driver, By.NAME, "btnLogIn")
    
    # Check if login was successful
    if "login.do" in driver.current_url:
        logging.error("Login failed - still on login page")
        raise Exception("Login failed")
    
    logging.info("Login successful.")

def navigate_to_fare_search(driver):
    # Direct URL navigation is more reliable
    try:
        navigate_to_page(driver, "https://www.expertflyer.com/air/fareInformation.do")
        time.sleep(1)  # Allow page to stabilize
    except Exception as e:
        logging.error(f"Failed to navigate to fare search: {e}")
        # Try clicking the menu item as fallback
        try:
            fare_menu = driver.find_element(By.XPATH, "//a[text()='Fare Information']")
            fare_menu.click()
        except Exception as inner_e:
            logging.error(f"Both navigation methods failed: {inner_e}")
            raise

def calculate_dates(depart_date):
    # Set return date to Tuesday following the Wednesday departure
    return_date = depart_date + timedelta(days=6)
    
    # Calculate ticketing date (3 months before departure)
    ticketing_date = depart_date - timedelta(days=90)
    
    # Check if ticketing date is more than a year in the past
    today = date.today()
    one_year_ago = today - timedelta(days=365)
    if ticketing_date < one_year_ago:
        ticketing_date = one_year_ago
    
    return return_date, ticketing_date

def format_date(date_obj):
    return date_obj.strftime("%m/%d/%Y")

def fill_fare_search_form(driver, depart_date, return_date, ticketing_date):
    depart_date_str = format_date(depart_date)
    return_date_str = format_date(return_date)
    ticketing_date_str = format_date(ticketing_date)
    
    logging.info(f"Searching with depart: {depart_date_str}, return: {return_date_str}, ticketing: {ticketing_date_str}")
    
    # Fill form fields
    try:
        enter_text(driver, By.NAME, "departingAirport", "Taipei, Taiwan, Taiwan Taoyuan International Airport (TPE)")
        enter_text(driver, By.NAME, "arrivingAirport", "San Francisco, CA, USA, San Francisco International Airport (SFO)")
        enter_text(driver, By.NAME, "purchasingAirport", "Taipei, Taiwan, Taiwan Taoyuan International Airport (TPE)")
        enter_text(driver, By.NAME, "departDate", depart_date_str)
        enter_text(driver, By.NAME, "returnDate", return_date_str)
        enter_text(driver, By.NAME, "airline", "China Airlines (CI)")
        enter_text(driver, By.NAME, "ticketingDate", ticketing_date_str)
        
        # Set dropdowns
        select_dropdown(driver, By.NAME, "passengerType", 0)  # Adult
        select_dropdown(driver, By.NAME, "currencyCode", 45)  # USD
        select_dropdown(driver, By.NAME, "cabin", 0)          # Any
    except Exception as e:
        logging.error(f"Error filling form: {e}")
        driver.save_screenshot(f"form_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        raise

def submit_search(driver):
    try:
        click_element(driver, By.NAME, "btnSearch")
        logging.info("Search submitted successfully.")
        
        # Wait for search results to load
        time.sleep(1)  # Use a timeout
    except Exception as e:
        logging.error(f"Error submitting search: {e}")
        driver.save_screenshot(f"search_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        raise

def download_results(driver):
    try:
        # Try to find and click the Share Results button
        try:
            share_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Share Results')]")
            share_button.click()
            logging.info("Share Results button clicked.")
        except:
            logging.warning("Could not find Share Results button by text, trying alternate method")
            try:
                share_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div[2]/form/span[2]/a")
                share_button.click()
                logging.info("Share Results button clicked via XPath.")
            except Exception as e:
                logging.error(f"Failed to click Share Results button: {e}")
                driver.save_screenshot("share_button_error.png")
                raise
        

        # Try to find and click the Download as File button
        try:
            download_button = driver.find_element(By.XPATH, "//input[@value='Download as File']")
            download_button.click()
            logging.info("Download as File button clicked.")
        except:
            logging.warning("Could not find Download button by value, trying alternate method")
            try:
                download_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div[2]/div[2]/form/div[3]/input[3]")
                download_button.click()
                logging.info("Download as File button clicked via XPath.")
            except Exception as e:
                logging.error(f"Failed to click Download button: {e}")
                driver.save_screenshot("download_button_error.png")
                raise
        
        logging.info("Results downloaded successfully.")
        
    except Exception as e:
        logging.error(f"Error downloading results: {e}")
        driver.save_screenshot(f"download_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        raise

def main():
    driver = None
    try:
        driver = setup_browser()
        username = "andrewpan0729@gmail.com"
        password = "apresearch"
        
        # Login
        login_to_expertflyer(driver, username, password)
        
        # Set start date to March 27, 2024 (Wednesday)
        start_date = datetime(2024, 3, 27).date()
        end_date = datetime(2025, 3, 12).date()
        
        current_date = start_date
        
        while current_date <= end_date:
            try:
                # Calculate return and ticketing dates
                return_date, ticketing_date = calculate_dates(current_date)
                
                # Navigate to fare search page
                navigate_to_fare_search(driver)
                
                # Fill form with current dates
                fill_fare_search_form(driver, current_date, return_date, ticketing_date)
                
                # Submit search
                submit_search(driver)
                
                # Download results
                download_results(driver)
                
                # Move to next Wednesday
                current_date += timedelta(days=7)
                
                logging.info(f"Completed search for {format_date(current_date - timedelta(days=7))}. Moving to next date.")
                
            except Exception as e:
                logging.error(f"Error in iteration for date {format_date(current_date)}: {e}")
                driver.save_screenshot(f"iteration_error_{current_date.strftime('%Y%m%d')}.png")
                
                # Try to recover by going back to the fare search page
                try:
                    navigate_to_page(driver, "https://www.expertflyer.com/air/fareInformation.do")
                    # Move to next date regardless of error
                    current_date += timedelta(days=7)
                    logging.info(f"Recovered from error. Moving to next date: {format_date(current_date)}")
                except:
                    logging.error("Could not recover from error. Exiting.")
                    break
            
            # Short pause between iterations
            time.sleep(1)
            
        logging.info("All searches completed.")

    except Exception as e:
        logging.error(f"An error occurred in main process: {e}")
        if driver:
            driver.save_screenshot(f"error_main_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed.")

if __name__ == "__main__":
    main()