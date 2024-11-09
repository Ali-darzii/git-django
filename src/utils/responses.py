from rest_framework.permissions import BasePermission


class ErrorResponses:
    BAD_FORMAT = {'detail': 'BAD_FORMAT', 'error_code': 1, "status":False}
    OBJECT_NOT_FOUND = {'detail': 'OBJECT_NOT_FOUND', 'error_code': 2, "status":False}
    WRONG_LOGIN_DATA = {'detail': 'WRONG_USER_LOGIN_DATA', 'error_code': 3, "status":False}
    MISSING_PARAMS = {'detail': 'MISSING_PARAMS', 'error_code': 4, "status":False}
    TOKEN_IS_EXPIRED_OR_INVALID = {'detail': 'TOKEN_IS_EXPIRED_OR_INVALID', 'error_code': 5, "status":False}
    CODE_IS_EXPIRED_OR_INVALID = {'detail': 'CODE_IS_EXPIRED_OR_INVALID', 'error_code': 6, "status":False}
    SOMETHING_WENT_WRONG = {'detail': "WE_ALSO_DON'T_KNOW_WHAT_HAPPENED!", 'error_code': 7, "status":False}
    USER_IS_NOT_ACTIVE = {'detail': "USER_IS_NOT_ACTIVE", 'error_code': 8, "status":False}



class NotAuthenticated(BasePermission):
    message = "Client could not be authenticated."

    def has_permission(self, request, view):
        if request.headers.get("Authorization") is not None:
            return False
        return True
