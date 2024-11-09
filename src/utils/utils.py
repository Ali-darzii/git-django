import random

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def otp_code_generator():
    return random.randint(10000000, 99999999)


def create_user_agent(request):
    return {
        "device_name": request.user_agent.device.family,
        "is_phone": request.user_agent.is_mobile,
        "browser": request.user_agent.browser.family,
        "os": request.user_agent.os.family
    }

