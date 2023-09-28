import json
import datetime as dt

import apprise
import requests


def toggle_keka_attendance(org, headers, locationAddress, punchStatus):
    method = "POST"
    url = f"https://{org}.keka.com/k/dashboard/api/mytime/attendance/webclockin"

    payload = {
        "timestamp": (dt.datetime.now() - dt.timedelta(hours=5, minutes=30)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "attendanceLogSource": 1,
        "locationAddress": locationAddress,
        "manualClockinType": 1,
        "note": "",
        "originalPunchStatus": punchStatus # 0 for clock-in, 1 for clock-out
    }

    response = requests.request(
        method, 
        url, 
        headers=headers, 
        json=payload
        )
    return response


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

    method = "GET"
    url = f"https://{org}.keka.com/k/dashboard/api/mytime/attendance/attendancedayrequests"
    response = requests.request(
        method,
        url,
        headers=headers,
        )
    if response.status_code == requests.codes.ok:
        data = response.json()
    else:
        print(response.status_code)
        print(response.text)
        apobj.notify(title="Keka Attendance", body="Token Expired")
        raise Exception("Token Expired")
    # with open("response_data.json", "w") as f:
    #     f.write(json.dumps(data, indent=4))

    if data['data']['webclockinLastEntry']:
        punchStatus = data['data']['webclockinLastEntry']['punchStatus']
    else:
        punchStatus = 1

    # if punchStatus:
    #     print("Keka already clocked-out, clocking in")
    # else:
    #     print("Keka already clocked-in, clocking out")

    response = toggle_keka_attendance(org, headers, locationAddress, not punchStatus)
    return response, punchStatus


with open('config.json') as f:
    config = json.load(f)

apobj = apprise.Apprise()


for item in config.values():
    if item.get("pbul_access_token"):
        apobj.add(f"pbul://{item['pbul_access_token']}", tag='pbul')

    response, punchStatus = keka_attendance(
        org=item['org'], 
        access_token=item['access_token'], 
        locationAddress=item.get('locationAddress')
        )

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
