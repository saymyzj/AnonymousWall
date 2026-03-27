from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from common.exceptions import APIResponse
from .serializers import RegisterSerializer, UpdatePreferencesSerializer, UserInfoSerializer
from .utils import generate_avatar_seed, generate_nickname


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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_preferences(request):
    serializer = UpdatePreferencesSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return APIResponse(data=UserInfoSerializer(request.user).data, message='偏好已更新')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    from apps.comments.serializers import CommentSerializer
    from apps.interactions.models import Favorite
    from apps.posts.serializers import PostListSerializer

    all_posts = [post for post in request.user.posts.filter(is_deleted=False).select_related('identity').order_by('-created_at') if not post.is_expired]
    posts_qs = all_posts[:12]
    comments_qs = request.user.comments.select_related('post', 'parent').order_by('-created_at')[:8]
    favorite_ids = Favorite.objects.filter(user=request.user, target_type='post').values_list('target_id', flat=True)
    favorite_posts = (
        request.user.__class__.objects.none()
    )
    from apps.posts.models import Post
    favorite_posts = [
        post for post in Post.objects.filter(pk__in=favorite_ids, is_deleted=False).select_related('identity').order_by('-created_at')
        if not post.is_expired
    ][:8]

    comment_user_map_cache = {}
    comment_data = []
    for comment in comments_qs:
        if comment.post_id not in comment_user_map_cache:
            ordered_ids = (
                comment.post.comments
                .filter(status__in=['normal', 'ai_suspect'])
                .order_by('created_at')
                .values_list('author_id', flat=True)
            )
            mapping = {}
            for author_id in ordered_ids:
                if author_id not in mapping:
                    mapping[author_id] = len(mapping)
            comment_user_map_cache[comment.post_id] = mapping

        comment_data.append(
            CommentSerializer(
                comment,
                context={
                    'request': request,
                    'user_map': comment_user_map_cache[comment.post_id],
                    'post_author_id': comment.post.author_id,
                },
            ).data
        )

    data = {
        'posts': PostListSerializer(posts_qs, many=True, context={'request': request}).data,
        'comments': comment_data,
        'favorites': PostListSerializer(favorite_posts, many=True, context={'request': request}).data,
        'stats': {
            'post_count': len(all_posts),
            'comment_count': request.user.comments.count(),
            'favorite_count': Favorite.objects.filter(user=request.user, target_type='post').count(),
        },
    }
    return APIResponse(data=data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_identity(request):
    identity = request.user.identities.create(
        nickname=generate_nickname(),
        avatar_seed=generate_avatar_seed(),
    )
    request.user.refresh_from_db()
    return APIResponse(
        data=UserInfoSerializer(request.user).data,
        message='匿名身份已刷新',
    )
