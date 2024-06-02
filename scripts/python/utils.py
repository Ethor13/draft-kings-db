import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict
import csv

COOKIES_DIR = "tmp/"


def send_email(
    sender_email: str,
    sender_password: str,
    recipient_email: str,
    subject: str,
    body: str,
    smtp_server: str = "smtp.office365.com",
    port: int = 587,
):
    """
    Sends an email.

    Parameters:
    - sender_email: Sender's email address
    - sender_password: Sender's email password
    - recipient_email: Recipient's email address
    - subject: Email subject
    - body: Email body (plain text or HTML)
    - smtp_server: SMTP server address
    - port: SMTP server port
    """
    # Create Email Message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Try to send Email
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def netscape_cookies(cookies: List[Dict]):
    # http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt
    netscaped = []
    for cookie in cookies:
        fields = [
            cookie["domain"],
            "TRUE" if cookie["domain"][0] == "." else "FALSE",
            cookie["path"],
            "TRUE" if cookie["secure"] else "FALSE",
            cookie.get("expires", 0),
            cookie["name"],
            cookie["value"],
        ]
        netscaped.append(fields)
    return netscaped


def write_cookies(cookies: List[Dict]):
    nc = netscape_cookies(cookies)
    cookie_file_header = [
        ["# Netscape HTTP Cookie File"],
        ["# http://curl.haxx.se/rfc/cookie_spec.html"],
        ["# This is a generated file!  Do not edit."],
        [],
    ]

    with open(COOKIES_DIR + "cookies.txt", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cookie_file_header)
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(nc)
