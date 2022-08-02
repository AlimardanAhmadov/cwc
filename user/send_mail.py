from django.conf import settings
from celery import shared_task

from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


from django.contrib.auth import get_user_model

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

User = get_user_model()

url = "http://localhost:8000/"


@shared_task(bind=True, max_retries=20)
def send_register_mail(self, user, key):
    body = """<p>
    Hello from CWC!<br><br>

    Confirmation Mail: %s

    You can see more details in this link: %saccount-confirm-email/%s<br><br>

    Thank you from E-commerce! <br><br>
    <p>""" % (
        user.username,
        url,
        key,
    )

    subject = "Registeration Mail"
    recipients = [user.email]

    try:
        send_email(body, subject, recipients, "html")
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)
        raise self.retry(exc=e, countdown=25200)


@shared_task(bind=True, max_retries=1)
def send_reset_password_email(self, user_id):
    user = User.objects.get(id=user_id)
    body = """
    %spassword/reset/confirm/%s/%s
    """ % (
        url,
        urlsafe_base64_encode(force_bytes(user.pk)),
        default_token_generator.make_token(user),
    )
    print(body)
    subject = "Reset password Mail"
    recipients = [user.email]
    try:
        send_email(body, subject, recipients, "html")
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)
        raise self.retry(exc=e, countdown=25200)


def send_email(body, subject, recipients, body_type="plain"):
    mail_subject = subject
    content = render_to_string('email/reset_password.html', {
        'body': body
    })
    message = Mail(
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to_emails=recipients,
        subject=mail_subject,
        html_content=content
    )

    try:
        sg = SendGridAPIClient(getattr(settings, "SENDGRID_API_KEY", None))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return response
    except Exception as e:
        print("error: ",e)

