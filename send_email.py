import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random


def send_email(to_email, subject, text):
    from_email = 'MS_4JTXDW@trial-r83ql3pwjozgzw1j.mlsender.net'
    password = 'mssp.nlJUVvZ.z86org8o27k4ew13.PVlAkvb'

    server= "smtp.mailersend.net"
    port= 587
    my_server = smtplib.SMTP(server, port)
    my_server.ehlo()
    my_server.starttls()

    my_server.login(from_email, password)

    message = MIMEMultipart("alternative")

    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(text))

    my_server.sendmail(
                    from_addr= from_email,
                    to_addrs = to_email,
                    msg=message.as_string()
                )
    
def send_email_to_recover_password(to_email, link):
    subject = 'CRIME TRACKER'
    text = f'Щоб скинути пароль перейдіть за посиланням:\n{link}'
    send_email(to_email, subject, text)

def send_email_to_confirm(to_email):
    subject = 'CRIME TRACKER'
    code = random.randint(100000, 999999)
    text = f'Ваш код для підтвердження електронної скриньки:\n{code}'
    send_email(to_email, subject, text)
    return code