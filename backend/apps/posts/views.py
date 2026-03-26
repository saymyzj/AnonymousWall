from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from common.exceptions import APIResponse
from common.pagination import StandardPagination
from .models import Post
from .serializers import PostListSerializer, PostDetailSerializer, CreatePostSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def post_list(request):
    queryset = Post.objects.filter(
        is_deleted=False,
        status__in=['normal', 'ai_suspect'],
    ).select_related('identity')

    # Tag filter
    tag = request.query_params.get('tag')
    if tag:
        queryset = queryset.filter(tag=tag)

    # Time filter
    time_filter = request.query_params.get('time')
    if time_filter == 'today':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=1))
    elif time_filter == 'week':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
    elif time_filter == 'month':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))

    # Sort
    sort = request.query_params.get('sort', 'latest')
    if sort == 'hot':
        queryset = queryset.extra(
            select={'hot_score': 'like_count * 2 + comment_count * 3 + favorite_count * 1'},
        ).order_by('-hot_score', '-created_at')
    else:
        queryset = queryset.order_by('-created_at')

    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = PostListSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    serializer = CreatePostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # L1: Sensitive word check
    from apps.moderation.services import check_content
    content = serializer.validated_data['content']
    is_blocked, is_suspect, hard_words, soft_words = check_content(content)
    if is_blocked:
        return APIResponse(
            code=400,
            message=f'内容包含违禁词：{"、".join(hard_words)}，请修改后重新发布',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    identity = request.user.identities.order_by('-created_at').first()
    post_status = 'ai_suspect' if is_suspect else 'normal'
    post = serializer.save(author=request.user, identity=identity, status=post_status)
    return APIResponse(
        data=PostDetailSerializer(post, context={'request': request}).data,
        message='发布成功',
        status_code=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def post_detail(request, pk):
    try:
        post = Post.objects.select_related('identity').get(pk=pk, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)
    serializer = PostDetailSerializer(post, context={'request': request})
    return APIResponse(data=serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, pk):
    try:
        post = Post.objects.get(pk=pk, author=request.user, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)
    post.is_deleted = True
    post.save(update_fields=['is_deleted'])
    return APIResponse(message='删除成功')
