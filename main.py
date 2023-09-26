import json
import datetime as dt

import apprise
import requests


def keka_attendance(org, access_token, locationAddress=None):
    headers = {
        'authority': f'{org}.keka.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {access_token}',
        'cache-control': 'no-cache',
        'content-type': 'application/json; charset=UTF-8',
        'origin': f'https://{org}.keka.com',
        'pragma': 'no-cache',
        'referer': f'https://{org}.keka.com/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    cookies = {
        'Subdomain': f'{org}.keka.com',
        '_ga': 'GA1.1.835467246.1675746350',
        '_ga_9XJPTJPZEE': 'GS1.1.1676888005.10.1.1676888391.0.0.0',
        'ai_user': 'EdsIhbarLWlBBURy3IWMa0|2023-06-26T04:41:14.723Z',
        '_clck': 'kvskda|2|ff8|0|1227',
        '_clsk': 'fk1q8x|1695357999329|1|0|v.clarity.ms/collect',
        'ai_session': 'kw7ublF2plJqPq5FJ4Q+Wg|1695357989703|1695357989703',
    }

    method = "GET"
    url = f"https://{org}.keka.com/k/dashboard/api/mytime/attendance/attendancedayrequests"
    response = requests.request(
        method, 
        url, 
        headers=headers, 
        cookies=cookies
        )
    data = response.json()

    if data['data']['webclockinLastEntry']:
        punchStatus = data['data']['webclockinLastEntry']['punchStatus']
    else:
        punchStatus = 1

    # if punchStatus:
    #     print("Keka already clocked-out, clocking in")
    # else:
    #     print("Keka already clocked-in, clocking out")

    method = "POST"
    url = f"https://{org}.keka.com/k/dashboard/api/mytime/attendance/webclockin"

    payload = {
        "timestamp": (dt.datetime.now() - dt.timedelta(hours=5, minutes=30)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "attendanceLogSource": 1,
        "locationAddress": locationAddress,
        "manualClockinType": 1,
        "note": "",
        "originalPunchStatus": not punchStatus # 0 for click-in, 1 for clock-out
    }

    response = requests.request(
        method, 
        url, 
        headers=headers, 
        cookies=cookies, 
        json=payload
        )
    return response, punchStatus


with open('config.json') as f:
    config = json.load(f)

for item in config.values():
    response, punchStatus = keka_attendance(
        org=item['org'], 
        access_token=item['access_token'], 
        locationAddress=item.get('locationAddress')
        )

    apobj = apprise.Apprise()
    if item.get("pbul_access_tokens"):
        apobj.add(f"pbul://{item['pbul_access_token']}", tag='pbul')

    if response.status_code == requests.codes.ok:
        if punchStatus:
            print("clocked-in")
            apobj.notify(title="Keka Attendance", body="clocked-in")
        else:
            print("clocked-out")
            apobj.notify(title="Keka Attendance", body="clocked-out")

        with open('response_data.json', 'w') as f:
            json.dump(response.json(), f, indent=4)
    else:
        print('failed')
        apobj.notify(title="Keka Attendance", body="Keka attendance bot failed")
