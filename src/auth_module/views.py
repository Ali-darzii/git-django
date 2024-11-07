# from rest_framework.views import APIView
# from rest_framework.response import Response
# from auth_module.models import User
# from auth_module.serializers import EmailCheckSerializer
# from utils.responses import NotAuthenticated, ErrorResponses
# from utils.throttling import EmailCheckThrottle
# from rest_framework import status
#
#
# class EmailView(APIView):
#     permission_classes = [NotAuthenticated]
#
#     def post(self, request):
#         """ Is Email Available  """
#         serializer = EmailCheckSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             User.objects.get(email=serializer.validated_data.get("email"))
#         except User.DoesNotExist:
#             return Response(data={"detail": "Not found.", "status": True}, status=status.HTTP_404_NOT_FOUND)
#         return Response(data={"detail": "User exist.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
#
#     def put(self, request):
#         """ User Register """
#
#     def get_throttles(self):
#         if self.request.method == "POST":
#             self.throttle_classes = EmailCheckThrottle
#         else:
#             # for put
#             self.throttle_classes = []
#         return super(EmailView, self).get_throttles()
#
#
# # email otp no JWT return