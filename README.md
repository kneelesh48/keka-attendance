# Automate Keka Attendance

### Install Chrome
* `apt install libappindicator1 fonts-liberation`
* `wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb`
* `dpkg -i google-chrome*.deb`
* Test Chrome installation `google-chrome-stable -version`
* Test running Chrome `google-chrome-stable --headless --no-sandbox --disable-gpu --print-to-pdf https://google.com`

### Install chromedriver
* Visit this page for latest chromedriver https://googlechromelabs.github.io/chrome-for-testing
* `wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chromedriver-linux64.zip`
* `unzip chromedriver-linux64.zip`
* `mv chromedriver-linux64/chromedriver /usr/local/bin`


### Steps to Install
1. Clone the repo `git clone https://github.com/kneelesh48/keka-attendance.git`
2. Install required packages `pip install -r requirements.txt`
3. Rename `config.example.json` to `config.json` and add fill in your details. 
    * `org` and `access_token` are mandatory, `locationAddress` and `pbul_access_token` are optional
    * Org can be found in the keka url
    * Login to Keka and run the following JavaScript in Chrome DevTools Console to obtain keka access token `localStorage.getItem("access_token")`

### Steps to Run via Selenium
* `python3 app-selenium.py` toggle clock-in/clock-out
* `python3 app-selenium.py clock-in`
* `python3 app-selenium.py clock-out`

### Steps to Run via API
* Run the application by `python3 app-api.py`


Add the application to crontab on linux or Task Scheduler on Windows to automate your attendance.
