# Ref. https://mailtrap.io/blog/python-send-email-gmail/
import smtplib
from email.mime.text import MIMEText
sender = "caliberai123@gmail.com" #From
recipients = ["deshmukharpit772@gmail.com"] # To
# load_dotenv() # Load variables from .env file
password = "ucoz pkvc cumx moak"

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    return 1
    print("Email sent successfully!")

send_email("subject 1", "Hi", sender, recipients, password)
