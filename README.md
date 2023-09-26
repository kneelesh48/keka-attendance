# Automate Keka Attendance

### Steps to Install
1. Clone the repo `git clone https://github.com/kneelesh48/keka-attendance.git`
2. Install required packages `pip install -r requirements.txt`
3. Rename config.example.json to config.json and add fill in your details. `org` and `access_token` are mandatory, `locationAddress` and `pbul_access_token` are optional
    * Org can be found in the keka url
    * Login to Keka and run the following JavaScript in Chrome Dev tools Console to obtain keka access token `localStorage.getItem("access_token")`

### Steps to Run
* Run the application by `python main.py`


Add the application to crontab on linux or Task Scheduler on Windows to automate your attendance.
