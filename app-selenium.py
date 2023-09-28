import sys
import json
import datetime as dt

import apprise
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC


opt = None
if len(sys.argv) > 1:
    opt = sys.argv[1]


def selenium_prep(profile_directory):
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
    options.add_argument(f"profile-directory={profile_directory}")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    return driver


def clockin():
    driver.find_element(By.XPATH, "//*[contains(text(), 'Web Clock-In')]").click()
    driver.find_element(By.XPATH, "//*[contains(text(), 'Cancel')]").click() # Cancel allow location
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Clock-out')]")))
    driver.save_screenshot(f"Screenshots/{dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}-clockin.png")
    print("clocked-in")
    apobj.notify(title="Keka Attendance", body="clocked-in")


def clockout():
    driver.find_element(By.XPATH, "//*[contains(text(), 'Clock-out')]").click()
    driver.find_element(By.XPATH, "//*[contains(text(), 'Clock-out')]").click()
    driver.find_element(By.XPATH, "//*[contains(text(), 'Cancel')]").click() # Cancel allow location
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Web Clock-In')]")))
    driver.save_screenshot(f"Screenshots/{dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}-clockout.png")
    print("clocked-out")
    apobj.notify(title="Keka Attendance", body="clocked-out")


with open('config.json') as f:
    config = json.load(f)

apobj = apprise.Apprise()


for item in config.values():
    if item.get("pbul_access_token"):
        apobj.add(f"pbul://{item['pbul_access_token']}", tag='pbul')

    driver = selenium_prep(item["profile_directory"])

    driver.get("https://sedin.keka.com/#/home/dashboard")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "home-attendance-clockin-widget button")))
    print("Page loaded!")

    text = driver.find_element(By.CSS_SELECTOR, "home-attendance-clockin-widget button").text

    if opt:
        if opt == 'clock-in' and text == "Web Clock-In":
            clockin()
        elif opt == 'clock-out' and text == "Clock-out":
            clockout()
        else:
            print(f"{opt} already done")
            apobj.notify(title="Keka Attendance", body=f"{opt} already done")
    else:
        if text == "Web Clock-In":
            clockin()

        elif text == "Clock-out":
            clockout()

    driver.quit()
