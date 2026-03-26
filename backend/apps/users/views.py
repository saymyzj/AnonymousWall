from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from common.exceptions import APIResponse
from .serializers import RegisterSerializer, UserInfoSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return APIResponse(
        data={
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserInfoSerializer(user).data,
        },
        message='注册成功',
        status_code=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return APIResponse(code=400, message='请输入邮箱和密码', status_code=status.HTTP_400_BAD_REQUEST)
    user = authenticate(request, email=email, password=password)
    if user is None:
        return APIResponse(code=401, message='邮箱或密码错误', status_code=status.HTTP_401_UNAUTHORIZED)
    if user.is_banned:
        from django.utils import timezone
        if user.ban_until and user.ban_until > timezone.now():
            return APIResponse(code=403, message=f'账号已被禁言至 {user.ban_until.strftime("%Y-%m-%d")}', status_code=status.HTTP_403_FORBIDDEN)
        else:
            user.is_banned = False
            user.ban_until = None
            user.save(update_fields=['is_banned', 'ban_until'])
    refresh = RefreshToken.for_user(user)
    return APIResponse(data={
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserInfoSerializer(user).data,
    }, message='登录成功')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return APIResponse(data=UserInfoSerializer(request.user).data)
