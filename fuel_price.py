import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import re

# ========== SETTINGS (filled by GitHub Secrets) ==========
URL = "https://netcong.libertydiscountfuel.com/product/heating-oil/"
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]
# ========================================================

def get_prices():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    online_el = soup.select_one("p.online-price")
    normal_el = soup.select_one("p.normal-price")

    if not online_el:
        raise Exception("Could not find the Online Price on the page")

    def clean_price(text):
        numbers = re.findall(r"[\d.]+", text)
        if not numbers:
            raise Exception(f"Could not parse price from: {text}")
        return float(numbers[0])

    online_price = clean_price(online_el.get_text())
    normal_price = clean_price(normal_el.get_text()) if normal_el else None

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
        now = datetime.now(ZoneInfo("America/New_York")).strftime("%A, %B %d, %Y at %I:%M %p")

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
