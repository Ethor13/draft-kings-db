from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from dotenv import load_dotenv
import os
import csv
import sys

load_dotenv()
login_url = "https://myaccount.draftkings.com/login"
TIMEOUT = 20

def login(driver):
    driver.get(login_url)

    username = driver.find_element(By.ID, "login-username-input")
    password = driver.find_element(By.ID, "login-password-input")
    submit = driver.find_element(By.ID, "login-submit")

    username.send_keys(os.getenv("DK_USERNAME"))
    password.send_keys(os.getenv("DK_PASSWORD"))
    submit.submit()


def netscape_cookies(cookies):
    # http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt
    netscaped = []
    for cookie in cookies:
        fields = [
            cookie["domain"],
            "TRUE" if cookie["domain"][0] == "." else "FALSE",
            cookie["path"],
            "TRUE" if cookie["secure"] else "FALSE",
            cookie.get("expiry", 0),
            cookie["name"],
            cookie["value"],
        ]
        netscaped.append(fields)
    return netscaped


def write_cookies(driver):
    nc = netscape_cookies(driver.get_cookies())
    cookie_file_header = [
        ["# Netscape HTTP Cookie File"],
        ["# http://curl.haxx.se/rfc/cookie_spec.html"],
        ["# This is a generated file!  Do not edit."],
        [],
    ]

    with open("tmp/cookies.txt", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cookie_file_header)
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(nc)


if __name__ == "__main__":
    options = Options()

    # headless automation
    # options.use_chromium = True
    # options.add_argument("headless")

    options.add_argument("--inprivate")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # try to hide "Edge is being controlled by automated software pop-up"
    options.add_argument("--disable-extensions")
    options.add_experimental_option("useAutomationExtension", False)

    # don't indicate that browser is controlled by automation, and don't log
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )

    # don't close window right away. Not needed in production
    # options.add_experimental_option("detach", True)

    # https://www.browserstack.com/docs/automate/selenium/handle-permission-pop-ups#python
    # block location pop-up
    options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.geolocation": 2}
    )

    driver = webdriver.Edge(
        options=options, 
        service=Service(EdgeChromiumDriverManager().install()),
    )
    
    login(driver)

    try:
        if WebDriverWait(driver, timeout=TIMEOUT).until(
            expected_conditions.title_is("DraftKings Lobby"),
            message=f"Timed out after {TIMEOUT} seconds",
        ):
            write_cookies(driver)
            print("Wrote cookies.txt successfully")
            driver.quit()
            exit(0)
        else:
            print(
                f"Redirected unexpectedly to page {driver.title} at {driver.current_url}",
                file=sys.stderr,
            )
            driver.quit()
            exit(1)

    except Exception as e:
        print(e, file=sys.stderr)
        driver.quit()
        exit(1)
