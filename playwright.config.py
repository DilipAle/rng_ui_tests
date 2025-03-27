import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from config.config import Config
from pages.login_page import LoginPage

# Load environment variables from the .env file
load_dotenv()

def run(playwright):
    # Get the environment and configuration details
    config = Config()

    # Use Chromium as the default browser (no need for dynamic selection anymore)
    browser = playwright.chromium.launch(headless= False)
    page = browser.new_page()

    # Navigate to the environment-specific URL
    page.goto(config.BASE_URL)

    # Create an instance of LoginPage and perform login
    login_page = LoginPage(page)
    login_page.login(config.USERNAME, config.PASSWORD)
    
    page.wait_for_selector("//span[@title = 'My Agency']", timeout=10000)  # waits for 10 seconds


    # Print the page title after login
    print(f"Page Title: {page.title()}")

    # Close the browser
    browser.close()

# Running Playwright with dynamic environment URL
with sync_playwright() as playwright:
    run(playwright)
