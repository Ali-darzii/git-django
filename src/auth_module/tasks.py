from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as Send_Email


@shared_task(queue="tasks")
def send_email(email, subject, body):
    for i in range(2):
        try:
            host_email = settings.EMAIL_HOST_USER
            Send_Email(subject, body, host_email, [email], fail_silently=False)
            break
        except Exception as e:
            pass
