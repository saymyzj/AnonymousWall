from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import F
from common.exceptions import APIResponse
from common.pagination import StandardPagination
from .models import Comment
from .serializers import CommentSerializer, CreateCommentSerializer
from apps.posts.models import Post


def _build_user_map(post_id):
    """Build a mapping of user_id -> index for anonymous labels within a post."""
    author_ids = (
        Comment.objects.filter(post_id=post_id, status__in=['normal', 'ai_suspect'])
        .order_by('created_at')
        .values_list('author_id', flat=True)
    )
    user_map = {}
    for uid in author_ids:
        if uid not in user_map:
            user_map[uid] = len(user_map)
    return user_map


@api_view(['GET'])
@permission_classes([AllowAny])
def comment_list(request, post_id):
    try:
        post = Post.objects.get(pk=post_id, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)

    queryset = Comment.objects.filter(
        post=post, status__in=['normal', 'ai_suspect']
    ).select_related('parent').order_by('created_at')

    user_map = _build_user_map(post_id)

    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = CommentSerializer(
        page, many=True,
        context={
            'request': request,
            'user_map': user_map,
            'post_author_id': post.author_id,
        }
    )
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    try:
        post = Post.objects.get(pk=post_id, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)

    serializer = CreateCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # L1: Sensitive word check
    from apps.moderation.services import check_content
    content = serializer.validated_data['content']
    is_blocked, is_suspect, hard_words, soft_words = check_content(content)
    if is_blocked:
        return APIResponse(
            code=400,
            message=f'评论包含违禁词：{"、".join(hard_words)}，请修改',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    parent = None
    parent_id = serializer.validated_data.get('parent_id')
    if parent_id:
        try:
            parent = Comment.objects.get(pk=parent_id, post=post)
        except Comment.DoesNotExist:
            return APIResponse(code=400, message='回复的评论不存在', status_code=status.HTTP_400_BAD_REQUEST)

    identity = request.user.identities.order_by('-created_at').first()
    comment_status = 'ai_suspect' if is_suspect else 'normal'
    comment = Comment.objects.create(
        post=post,
        author=request.user,
        identity=identity,
        parent=parent,
        content=serializer.validated_data['content'],
        status=comment_status,
    )
    Post.objects.filter(pk=post_id).update(comment_count=F('comment_count') + 1)

    user_map = _build_user_map(post_id)
    result = CommentSerializer(
        comment,
        context={
            'request': request,
            'user_map': user_map,
            'post_author_id': post.author_id,
        }
    ).data
    return APIResponse(data=result, message='评论成功', status_code=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, pk):
    try:
        comment = Comment.objects.get(pk=pk, author=request.user)
    except Comment.DoesNotExist:
        return APIResponse(code=404, message='评论不存在', status_code=status.HTTP_404_NOT_FOUND)
    post_id = comment.post_id
    comment.delete()
    Post.objects.filter(pk=post_id).update(comment_count=F('comment_count') - 1)
    return APIResponse(message='删除成功')
