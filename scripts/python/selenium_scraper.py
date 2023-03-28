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
COOKIES_DIR = "tmp/"
TIMEOUT = 60


def login(driver):
    driver.get(login_url)
    print(driver.title)

    try:
        WebDriverWait(driver, TIMEOUT).until(
            expected_conditions.presence_of_element_located(
                (By.ID, "login-username-input")
            )
        )
    except Exception as e:
        print("Couldn't find login form", e, file=sys.stderr)
        driver.quit()
        exit(1)

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

    with open(COOKIES_DIR + "cookies.txt", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cookie_file_header)
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(nc)


if __name__ == "__main__":
    options = Options()

    arguments = [
        "--inprivate",
        "--disable-blink-features=AutomationControlled",
        # try to hide "Edge is being controlled by automated software pop-up"
        "--disable-extensions",
    ]

    experimental_options = {
        "useAutomationExtension": False,
        # don't indicate that browser is controlled by automation, and don't log
        "excludeSwitches": ["enable-automation", "enable-logging"],
        # https://www.browserstack.com/docs/automate/selenium/handle-permission-pop-ups#python
        "prefs": {"profile.default_content_setting_values.geolocation": 2},
    }

    for argument in arguments:
        options.add_argument(argument)

    for experimental_option, value in experimental_options.items():
        options.add_experimental_option(experimental_option, value)

    driver_path = EdgeChromiumDriverManager(path=".").install()
    driver = webdriver.Edge(options=options, service=Service(driver_path))

    login(driver)

    try:
        WebDriverWait(driver, timeout=TIMEOUT).until(
            expected_conditions.url_changes(login_url),
            message=f"Timed out after {TIMEOUT} seconds",
        )
        if driver.title == "DraftKings Lobby":
            print(driver.title)
            print(driver.current_url)
            write_cookies(driver)
            print("Wrote cookies.txt successfully")
            driver.quit()
            exit(0)
        else:
            raise ValueError(
                f"Redirected unexpectedly to {driver.title} at {driver.current_url}"
            )

    except Exception as e:
        print(e, file=sys.stderr)
        driver.quit()
        exit(1)
