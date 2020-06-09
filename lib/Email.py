
from datetime import datetime
import lib.Accounts as Accounts
import smtplib
import time

class Email:
    def __init__(self, min_send_period_s):
        self.min_send_period_s = min_send_period_s
        self.last_run = datetime(2000, 1, 1, 0, 0, 0)

    def send_mail(self, recipient, subject, content):
        # abort if we sent an email too recently
        since_last_run = datetime.now() - self.last_run
        if since_last_run.seconds < self.min_send_period_s:
            return
        
        self.last_run = datetime.now()

        # create headers
        headers = ["From: " + Accounts.FROM_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        # connect to server
        session = smtplib.SMTP(Accounts.SMTP_SERVER, Accounts.SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        # login
        session.login(Accounts.FROM_USERNAME, Accounts.FROM_PASSWORD)

        # send email and disconnect
        session.sendmail(Accounts.FROM_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit

if __name__ == "__main__":
    sender = Email(5)

    sendTo = Accounts.TO_EMAIL
    emailSubject = "Hello World"
    emailContent = "This is a test"

    while True:
        sender.send_mail(sendTo, emailSubject, emailContent)
        time.sleep(1)
