from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from celery import shared_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import Payment

from django.contrib.auth import get_user_model

User = get_user_model()


url = "http://localhost:8000/"

@shared_task(bind=True, max_retries=1)
def create_payment_model(self, user_id, order_id):
    try:
        selected_user = get_object_or_404(User, id=user_id)
        if not Payment.objects.filter(user=selected_user).exists():
            new_payment = Payment(
                user=selected_user,
                order_id=order_id,
            )
            new_payment.save()
        else:
            selected_user.payment.order_id=order_id
            selected_user.payment.save()
    except  Exception as e:
        print(e)


@shared_task(bind=True, max_retries=1)
def recurring_payment_warning(self, id):
    user = User.objects.get(id=id)
    body = """
    %spurchase-subscription/
    """ % (
        url,
    )
    subject = "Make Payment"
    recipients = [user.email]
    try:
        send_email(body, subject, recipients, "html")
        if hasattr(user, 'profile'):
            user.profile.paid = False
            user.profile.save()

        elif hasattr(user, 'coach'):
            user.coach.paid = False
            user.coach.save()
        else:
            print("Nothing is happening")
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)
        raise self.retry(exc=e, countdown=25200)


def send_email(body, subject, recipients, body_type="plain"):
    mail_subject = subject
    content = render_to_string('email/payment.html', {
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

