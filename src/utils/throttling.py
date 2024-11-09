from rest_framework.throttling import SimpleRateThrottle


class NotAuthenticatedThrottle(SimpleRateThrottle):

    def get_ident(self, request):
        xci = request.META.get("X-Client-IP", None)
        return xci

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None  # Only throttle unauthenticated requests.

        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request)
        }


class RegisterEmailSendOTPThrottle(NotAuthenticatedThrottle):
    scope = "register_email_send_otp"


class IsActiveEmailSendOTPThrottle(NotAuthenticatedThrottle):
    scope = "is_active_email_send_otp"


class EmailCheckOTPThrottle(NotAuthenticatedThrottle):
    scope = "email_check_otp"
