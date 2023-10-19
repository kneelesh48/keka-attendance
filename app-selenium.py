import sys
import json
import datetime as dt

import apprise
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


opt = None
if len(sys.argv) > 1:
    opt = sys.argv[1]


def selenium_prep(display: bool = False, profile_directory: str = "Default"):
    options = webdriver.ChromeOptions()

    if display == False:
        options.add_argument("--headless")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--no-sandbox")
    elif display == True:
        options.add_argument("--start-maximized")

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


def ocr(ocr_space_apikey: str, image_base64: str):
    headers = {"apikey": ocr_space_apikey}

    payload = {
        "base64Image": image_base64,
        "scale": True,
        "language": "eng",
        "OCREngine": 2,
    }

    response = requests.post(
        "https://api.ocr.space/parse/image",
        headers=headers,
        data=payload,
    )

    captcha_text = response.json()["ParsedResults"][0]["ParsedText"]
    if captcha_text:
        captcha_text = captcha_text.split()[0]

    return captcha_text


def signin(keka_email: str, keka_password: str, ocr_space_apikey: str):
    driver.find_elements(By.CSS_SELECTOR, ".login-option button")[1].click()

    captcha_base64 = driver.find_element(By.CSS_SELECTOR, "#imgCaptcha").get_attribute("src")

    captcha_text = ""

    while not captcha_text:
        captcha_text = ocr(ocr_space_apikey=ocr_space_apikey, image_base64=captcha_base64)
        if not captcha_text:
            driver.refresh()

    driver.find_element(By.CSS_SELECTOR, "#email").send_keys(keka_email)
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys(keka_password)
    driver.find_element(By.CSS_SELECTOR, "#captcha").send_keys(captcha_text)
    driver.find_element(By.CSS_SELECTOR, "button").click()

    driver.find_element(By.XPATH, "//span[contains(text(), 'Send code to email')]").click()

    otp = input("Enter code sent to email")
    driver.find_element(By.CSS_SELECTOR, "input").send_keys(otp)
    driver.find_element(By.CSS_SELECTOR, "button").click()


def clockin():
    driver.find_element(By.XPATH, "//*[contains(text(), 'Web Clock-In')]").click()
    driver.find_element(By.XPATH, "//*[contains(text(), 'Cancel')]").click()  # Cancel allow location
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Clock-out')]")))
    driver.save_screenshot(f"Screenshots/{dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}-clockin.png")
    print("clocked-in")
    apobj.notify(title="Keka Attendance", body="clocked-in")


def clockout():
    driver.find_element(By.XPATH, "//*[contains(text(), 'Clock-out')]").click()
    driver.find_element(By.XPATH, "//*[contains(text(), 'Clock-out')]").click()
    driver.find_element(By.XPATH, "//*[contains(text(), 'Cancel')]").click()  # Cancel allow location
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Web Clock-In')]")))
    driver.save_screenshot(f"Screenshots/{dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}-clockout.png")
    print("clocked-out")
    apobj.notify(title="Keka Attendance", body="clocked-out")


with open("config.json") as f:
    config = json.load(f)


for item in config.values():
    apobj = apprise.Apprise()
    if item.get("pbul_access_token"):
        apobj.add(f"pbul://{item['pbul_access_token']}", tag="pbul")

    driver = selenium_prep(profile_directory=item["profile_directory"])

    driver.get(f"https://{item['org']}.keka.com/#/home/dashboard")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "home-attendance-clockin-widget button")))
    except Exception:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Login to Keka')]")))
        signin(
            keka_email=config["keka_email"],
            keka_password=config["keka_password"],
            ocr_space_apikey=config["ocr_space_apikey"],
        )
    print("Page loaded!")

    text = driver.find_element(By.CSS_SELECTOR, "home-attendance-clockin-widget button").text

    if opt:
        if opt == "clock-in" and text == "Web Clock-In":
            clockin()
        elif opt == "clock-out" and text == "Clock-out":
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
