from rest_framework.views import APIView
from rest_framework.response import Response
from auth_module.models import User
from auth_module.serializers import EmailCheckSerializer, UsernameCheckSerializer, SendOTPSerializer, CheckOTPSerializer
from utils.responses import NotAuthenticated, ErrorResponses
from rest_framework import status
from django.core.cache import cache as redis
from utils.throttling import EmailOTPPostThrottle, EmailOTPPutThrottle
from django.conf import settings
from .tasks import send_email
from utils.utils import otp_code_generator


class AvailableView(APIView):
    permission_classes = [NotAuthenticated]

    def post(self, request):
        """ Is Email Available  """
        serializer = EmailCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            User.objects.get(email=serializer.validated_data.get("email"))
        except User.DoesNotExist:
            return Response(data={"detail": "Not found.", "status": True}, status=status.HTTP_404_NOT_FOUND)
        return Response(data={"detail": "User exist.", "status": False}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """ Is Username Available """
        serializer = UsernameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            User.objects.get(username__iexact=serializer.validated_data.get("username"))
        except User.DoesNotExist:
            return Response(data={"detail": "Not found.", "status": True}, status=status.HTTP_404_NOT_FOUND)
        return Response(data={"detail": "User exist.", "status": False}, status=status.HTTP_400_BAD_REQUEST)


# email otp no JWT return
class RegisterEmailOTPView(APIView):
    permission_classes = [NotAuthenticated]

    def post(self, request):
        """ Register user with is_active=false and email otp """
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        otp_exp = settings.OTP_TIME_EXPIRE_DATA

        # handle user test
        if email == "example.for.test@gmail.com":
            token = "55555555"  # 8 * 5
            redis.set(f'{email}_otp', token)
            redis.expire(f'{email}_otp', otp_exp)
            return Response(data={'detail': 'Sent.'}, status=status.HTTP_201_CREATED)

        last_code = redis.get(f"{email}_code")
        if last_code is not None:
            return Response(data={'data': "not sent, please wait.", "status": False},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        token = otp_code_generator()
        redis.set(f"{email}_otp", token)
        redis.expire(f"{email}_otp", otp_exp)

        user = User.objects.create(
            email=serializer.validated_data.get("email"),
            username=serializer.validated_data.get("username"),
            is_active=False,
        )
        user.set_password(serializer.validated_data.get("password"))
        user.save()
        send_email.apply_async(args=(
            serializer.validated_data.get("email"),
            f"Your Git-Django launch code",
            f"Continue signing up for Git-Django by entering the code : {token}")
        )
        return Response(data={"data": "Sent.", "status": True}, status=status.HTTP_201_CREATED)

    def put(self, request):
        """ Registered user check otp and is_active=true """
        serializer = CheckOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data("email")
        tk = serializer.validated_data.get('tk')
        token = redis.get(f'{email}_otp')
        if token is None or int(tk) != token:
            return Response(data=ErrorResponses.TOKEN_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(
                email=email,
                is_active=False,
            )
        except User.DoesNotExist():
            return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        user.is_active = True
        user.save()
        return Response(data={"data": "User is active now.", "status": True}, status=status.HTTP_200_OK)

    def get_throttles(self):
        if self.request.method == "POST":
            self.throttle_classes = [EmailOTPPostThrottle]
        else:
            self.throttle_classes = [EmailOTPPutThrottle]
        return super(RegisterEmailOTPView, self).get_throttles()
