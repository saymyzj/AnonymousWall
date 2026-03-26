from rest_framework.permissions import BasePermission


class IsVerifiedUser(BasePermission):
    """Only allow verified users to perform write operations."""
    message = '您的账号尚未通过验证，暂时只能浏览内容'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )
