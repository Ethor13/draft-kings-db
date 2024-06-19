from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from dotenv import load_dotenv
from utils import write_cookies, send_email
import os
import re


load_dotenv()
LOGIN_URL = "https://myaccount.draftkings.com/login"
TIMEOUT = 60 * 1000


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(permissions=["geolocation"])
        context.set_default_timeout(TIMEOUT)

        page = context.new_page()

        # Apply stealth mode to the page
        stealth_sync(page)

        # Navigate to the DraftKings login page
        page.goto(LOGIN_URL)

        # Fill in the username and password
        page.fill("#login-username-input", os.getenv("DK_USERNAME"))
        page.fill("#login-password-input", os.getenv("DK_PASSWORD"))

        # Click the submit button
        page.click("#login-submit")

        # Wait for navigation
        # page.wait_for_load_state()
        # page.wait_for_url(re.compile("lobby"))
        page.wait_for_selector(".lobby")

        write_cookies(context.cookies(page.url))

        # Close the browser
        browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        send_email(
            os.getenv("SENDER_EMAIL"),
            os.getenv("SENDER_PASSWORD"),
            os.getenv("RECIPIENT_EMAIL"),
            "RIDDLER - Cookies could not be scraped from DraftKings",
            str(e.args),
        )
