from rest_framework.views import APIView
from rest_framework.response import Response
from auth_module.models import User
from auth_module.serializers import EmailCheckSerializer, UsernameCheckSerializer, SendOTPSerializer, \
    CheckOTPSerializer, LoginSerializer
from utils.responses import NotAuthenticated, ErrorResponses
from rest_framework import status
from django.core.cache import cache as redis
from utils.throttling import EmailCheckOTPThrottle, RegisterEmailSendOTPThrottle, IsActiveEmailSendOTPThrottle
from django.conf import settings
from .tasks import send_email, user_created_signal, user_login_failed_signal, user_login_signal
from utils.utils import otp_code_generator, get_client_ip, create_user_agent
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.permissions import IsAuthenticated

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
class EmailSendOTPView(APIView):
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
        redis.set(f"{email}_otp", token, otp_exp)

        user = User.objects.create(
            email=serializer.validated_data.get("email"),
            username=serializer.validated_data.get("username"),
            is_active=False,
        )
        user.set_password(serializer.validated_data.get("password"))
        user.save()
        user_created_signal.apply_async(args=(create_user_agent(request),get_client_ip(request), user.id))
        send_email.apply_async(args=(
            serializer.validated_data.get("email"),
            f"Your Git-Django launch code",
            f"Continue signing up for Git-Django by entering the code : {token}")
        )
        return Response(data={"data": "Sent.", "status": True}, status=status.HTTP_201_CREATED)

    def put(self, request):
        """send otp with email and password """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        if email is not None:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        else:
            username = serializer.validated_data.get("username")
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
            email = user.email
        if not user.check_password(serializer.validated_data.get("password")):
            return Response(data=ErrorResponses.WRONG_LOGIN_DATA, status=status.HTTP_400_BAD_REQUEST)

        last_code = redis.get(f"{email}_otp")
        if last_code is not None:
            return Response(data={'data': "not sent, please wait.", "status": False},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)
        token = otp_code_generator()
        otp_exp = settings.OTP_TIME_EXPIRE_DATA
        redis.set(f"{email}_otp", token, otp_exp)
        send_email.apply_async(args=(
            email,
            f"Your Git-Django launch code",
            f"Continue activating your Git-Django account by entering the code : {token}",)
        )
        return Response(data={"data": "Sent.", "status": True}, status=status.HTTP_200_OK)

    def get_throttles(self):
        if self.request.method == "POST":
            self.throttle_classes = [RegisterEmailSendOTPThrottle]
        else:
            self.throttle_classes = [IsActiveEmailSendOTPThrottle]
        return super(EmailSendOTPView, self).get_throttles()


@throttle_classes([EmailCheckOTPThrottle])
@permission_classes([NotAuthenticated])
@api_view(["POST"])
def check_email_otp(request):
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


class LogEmailView(APIView):

    def post(self, request):
        """ Login User(username or email and password) """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get("password")
        email = serializer.validated_data.get("email")

        if email is not None:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                user = User.objects.get(username=serializer.validated_data.get("username"))
            except User.DoesNotExist:
                return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
            email = user.email
        user_agent = create_user_agent(request)
        user_ip = get_client_ip(request)
        if not user.check_password(password):
            user_login_failed_signal.apply_async(args=(user_agent, user_ip, user.id))
            return Response(data=ErrorResponses.WRONG_LOGIN_DATA, status=status.HTTP_406_NOT_ACCEPTABLE)
        if not user.is_active:
            user_login_failed_signal.apply_async(args=(user_agent, user_ip, user.id))
            return Response(data=ErrorResponses.USER_IS_NOT_ACTIVE, status=status.HTTP_406_NOT_ACCEPTABLE)
        user.last_login = timezone.now()
        user.save()
        user_login_signal.apply_async(args=(user_agent, user_ip, user.id))
        data = {
            "access_token": str(AccessToken.for_user(user)),
            "refresh_token": str(RefreshToken.for_user(user)),
        }
        return Response(data=data, status=status.HTTP_202_ACCEPTED)

    def put(self, request):
        """ logout """
        try:
            refresh_token = request.data["refresh_token"]
            tk = RefreshToken(refresh_token)
            tk.blacklist()
        except Exception:
            return Response(data=ErrorResponses.TOKEN_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data={"data":"Successfully logged out.", "status":True}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request):
        """ User delete account """
        try:
            refresh_token = request.data["refresh_token"]
            tk = RefreshToken(refresh_token)
            tk.blacklist()
        except Exception:
            return Response(data=ErrorResponses.TOKEN_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)
        request.user.delete()
        return Response(data={"data":"Successfully deleted", "status":True}, status=status.HTTP_204_NO_CONTENT)
        
        
    
    
    
    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [NotAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]

        return super(LogEmailView, self).get_permissions()
