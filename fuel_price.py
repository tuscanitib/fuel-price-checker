import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo("America/New_York")).strftime("%A, %B %d, %Y at %I:%M %p")
import os

# ========== SETTINGS ==========
URL = "https://netcong.libertydiscountfuel.com/product/heating-oil/"

# These will come from GitHub Secrets later (or you can hard-code them for testing)
EMAIL_FROM = os.environ.get("EMAIL_FROM", "tuscanitib@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "jzmm hhwj such gcwh")
EMAIL_TO = os.environ.get("EMAIL_TO", "tuscanitib@gmail.com")
# ==============================

def get_prices():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    online = soup.select_one("p.online-price")
    normal = soup.select_one("p.normal-price")

    if not online:
        raise Exception("Could not find the Online Price")

    # Clean the price (handles the little raised 9)
    online_price = float(online.get_text().replace("Online Price:", "").replace("/gallon", "").replace("$", "").strip())
    
    normal_price = None
    if normal:
        normal_price = float(normal.get_text().replace("Normal Price:", "").replace("/gallon", "").replace("$", "").strip())

    return online_price, normal_price

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    try:
        online, normal = get_prices()
        now = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

        message = f"""Good morning!

Liberty Discount Fuel (Netcong) – Heating Oil Prices

Online Price:  ${online:.3f} per gallon
Normal Price:  ${normal:.3f} per gallon

Checked: {now}

Link: {URL}
"""
        print(message)
        send_email(f"Heating Oil Price: ${online:.3f}", message)

    except Exception as e:
        error_msg = f"Could not check the heating oil price today.\n\nError: {str(e)}"
        print(error_msg)
        send_email("Fuel Price Check Failed", error_msg)

if __name__ == "__main__":
    main()
