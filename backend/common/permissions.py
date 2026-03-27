from rest_framework.permissions import BasePermission
from django.utils import timezone


class IsVerifiedUser(BasePermission):
    """Only allow verified users to perform write operations."""
    message = '您的学号尚未通过管理员审核，当前仅可浏览内容'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_verified):
            return False

        if request.user.is_banned:
            if request.user.ban_until and request.user.ban_until <= timezone.now():
                request.user.is_banned = False
                request.user.ban_until = None
                request.user.save(update_fields=['is_banned', 'ban_until'])
                return True

            until = request.user.ban_until.strftime('%Y-%m-%d %H:%M') if request.user.ban_until else '永久'
            self.message = f'账号已被禁言，当前无法执行该操作。截止时间：{until}'
            return False

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )
