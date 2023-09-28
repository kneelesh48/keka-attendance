import sys
import datetime as dt

import apprise
from selenium import webdriver
from selenium.webdriver.common.by import By

opt = sys.argv[1]


def selenium_prep():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,720")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    options.add_argument("user-data-dir=/root/Selenium")
    options.add_argument("profile-directory=Default")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    return driver


apobj = apprise.Apprise()


driver = selenium_prep()

driver.get("https://sedin.keka.com/#/home/dashboard")

if opt == "clock-in":
    driver.find_element(By.CSS_SELECTOR, "home-attendance-clockin-widget button").click()
    driver.save_screenshot(f"Logs/screenshot-clockin-{dt.datetime.now().isoformat()}.png")
    apobj.notify(title="Keka Attendance", body="clocked-in")

if opt == "clock-out":
    driver.find_element(By.CSS_SELECTOR, "home-attendance-clockin-widget button").click()
    driver.find_element(By.CSS_SELECTOR, "home-attendance-clockin-widget button").click()
    driver.save_screenshot(f"Logs/screenshot-clockout-{dt.datetime.now().isoformat()}.png")
    apobj.notify(title="Keka Attendance", body="clocked-out")

driver.quit()
