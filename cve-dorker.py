import argparse
import os
import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Function to read JavaScript files from a text file
def read_js_files(file_path):
    with open(file_path, 'r') as file:
        js_files = file.readlines()
    # Remove whitespace characters like `\n` at the end of each line
    js_files = [js_file.strip() for js_file in js_files]
    return js_files

# Function to search for CVEs and take a screenshot
def search_and_screenshot(driver, js_file, output_folder):
    search_query = f"{js_file} CVE"
    logger.info(f"Searching for: {search_query}")
    driver.get("https://www.google.com")
    search_box = driver.find_element("name", "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    # Randomize delay
    delay = random.uniform(2, 5)  # Random delay between 2 to 5 seconds
    time.sleep(delay)

    try:
        # Wait for search results to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#search")))
    except TimeoutException:
        logger.warning("Search results did not load within 20 seconds.")

    # Randomly click on search results (simulate human behavior)
    search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
    if search_results:
        random_result = random.choice(search_results)
        random_result.click()

    # Scroll down the page (simulate human behavior)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Delay before taking the screenshot
    time.sleep(3)

    # Take screenshot
    screenshot_file = f"{os.path.splitext(os.path.basename(js_file))[0]}_cve.png"
    driver.save_screenshot(os.path.join(output_folder, screenshot_file))
    logger.info(f"Screenshot saved as {screenshot_file}")

# Main function
def main():
    parser = argparse.ArgumentParser(description='Search for CVEs related to JavaScript files and take screenshots of the search results.')
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the text file containing JavaScript file paths')
    parser.add_argument('-od', '--output-directory', type=str, default='screenshots', help='Directory to save screenshots (default: screenshots)')
    args = parser.parse_args()

    # Validate if the specified file exists
    if not os.path.exists(args.file):
        logger.error(f"The specified file '{args.file}' does not exist.")
        return

    # Initialize ChromeDriverManager for Chromium
    driver_path = ChromeDriverManager(chrome_type='chromium').install()  # Make sure ChromeDriverManager is installed

    # Configure Selenium WebDriver for Chromium
    chrome_options = Options()
    chrome_options.binary_location = '/usr/bin/chromium'  # <--- Change this to the correct path to Chromium binary on your system
    chrome_options.add_argument('--headless')  # Run in headless mode to avoid opening a browser window
    chrome_options.add_argument(f'user-agent={UserAgent().random}')  # Random user agent

    # Initialize WebDriver with Chromium options
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)

    js_files = read_js_files(args.file)  # Read JS files from the provided text file

    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    # Iterate over the list of JavaScript files
    for js_file in js_files:
        search_and_screenshot(driver, js_file, args.output_directory)

    # Close the WebDriver
    driver.quit()
    logger.info("WebDriver closed")

if __name__ == "__main__":
    main()
