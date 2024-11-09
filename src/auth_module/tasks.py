from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as Send_Email
from .models import UserLogins, UserIP, UserDevice



@shared_task(queue="tasks")
def send_email(email, subject, body):
    for i in range(2):
        try:
            host_email = settings.EMAIL_HOST_USER
            Send_Email(subject, body, host_email, [email], fail_silently=False)
            break
        except Exception as e:
            pass

@shared_task(queue="tasks")
def user_created_signal(user_agent, user_ip, user_id):
    user_logins = UserLogins.objects.create(user_id=user_id)
    UserIP.objects.create(user_logins=user_logins, ip=user_ip)
    device = UserDevice.get_user_device(user_agent, user_logins.id)
    device.save()
    return {"user_created": True}


@shared_task(queue="tasks")
def user_login_failed_signal(user_agent, user_ip, user_id):
    try:
        user_logins = UserLogins.objects.get(user_id=user_id)
        user_logins.failed_attempts += 1
        user_logins.save()
        UserIP.objects.create(user_logins=user_logins, ip=user_ip, failed=True)
        device = UserDevice.get_user_device(user_agent, user_logins.id)
        device.save()

        return {"user_logged_in_failed": True}
    except UserLogins.DoesNotExist:
        return {"user_logged_in_failed": False}
    
    
    
@shared_task(queue="tasks")
def user_login_signal(user_agent, user_ip, user_id):
    try:
        user_logins = UserLogins.objects.get(user_id=user_id)
        user_logins.no_logins += 1
        user_logins.save()
        UserIP.objects.create(user_logins=user_logins, ip=user_ip)
        devices = UserDevice.get_user_device(user_agent, user_logins.id)
        devices.save()
        return {"user_logged_in": True}
    except UserLogins.DoesNotExist:
        return {"user_logged_in": False}