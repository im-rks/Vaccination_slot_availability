import email
import smtplib
from datetime import datetime
import requests
import config

def create_session_info(center, session):
    return {"name": center["name"],
            "date": session["date"],
            "capacity": session["available_capacity"],
            "age_limit": session["min_age_limit"]}

def get_sessions(data):
    for center in data["centers"]:
        for session in center["sessions"]:
            yield create_session_info(center, session)

def is_available(session):
    return session["capacity"] > 0

def is_eighteen_plus(session):
    return session["age_limit"] == 18

def get_for_seven_days(start_date):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    params = {"district_id": 247, #change district_id here
    "date": start_date.strftime("%d-%m-%Y")}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0 Chrome 90.0.4430.212"}
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    return [session for session in get_sessions(data) if is_eighteen_plus(session) and is_available(session)]

def create_output(session_info):
    return f"{session_info['date']} - {session_info['name']} ({session_info['capacity']})"

print(get_for_seven_days(datetime.today()))
content = "\n".join([create_output(session_info) for session_info in get_for_seven_days(datetime.today())])
username = "" #from
to_user = [""] #recipient

if not content:
    print("No availability")
else:
    email_msg = email.message.EmailMessage()
    email_msg["Subject"] = "Vaccination Slot Open"
    email_msg["From"] = username
    email_msg["To"] = username
    email_msg.set_content(content)

    with smtplib.SMTP(host='smtp.gmail.com', port='587') as server:
        server.starttls()
        server.login(username, config.password)
        server.send_message(email_msg, username, to_user) 
