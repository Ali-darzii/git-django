from rest_framework.permissions import BasePermission


class ErrorResponses:
    BAD_FORMAT = {'detail': 'BAD_FORMAT', 'error_code': 1}
    OBJECT_NOT_FOUND = {'detail': 'OBJECT_NOT_FOUND', 'error_code': 2}
    WRONG_LOGIN_DATA = {'detail': 'WRONG_USER_LOGIN_DATA', 'error_code': 3}
    MISSING_PARAMS = {'detail': 'MISSING_PARAMS', 'error_code': 4}
    TOKEN_IS_EXPIRED_OR_INVALID = {'detail': 'TOKEN_IS_EXPIRED_OR_INVALID', 'error_code': 5}
    CODE_IS_EXPIRED_OR_INVALID = {'detail': 'CODE_IS_EXPIRED_OR_INVALID', 'error_code': 6}
    SOMETHING_WENT_WRONG = {'detail': "WE_ALSO_DON'T_KNOW_WHAT_HAPPENED!", 'error_code': 7}


class NotAuthenticated(BasePermission):
    message = "Client could not be authenticated."

    def has_permission(self, request, view):
        if request.headers.get("Authorization") is not None:
            return False
        return True
