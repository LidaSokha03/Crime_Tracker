import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
import random

def send_email(to_email, subject, text, name, surname):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = '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'

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email, "name": f"{name} {surname}"}],
        template_id=None, 
        subject=subject,
        html_content=f"<html><body><h1>{text}</h1></body></html>",
        text_content=text,
        sender={"name": "Crime Tracker", "email": "crimetracker2402@gmail.com"}
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        pprint(response)
        print("Лист успішно надіслано!")
    except ApiException as e:
        print("Виникла помилка при надсиланні:", e)

def send_email_to_confirm(to_email, name, surname):
    subject = 'CRIME TRACKER'
    code = random.randint(100000, 999999)
    text = f'Ваш код для підтвердження електронної скриньки:\n{code}'
    send_email(to_email, subject, text, name, surname)
    return code

