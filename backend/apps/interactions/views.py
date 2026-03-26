from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from common.exceptions import APIResponse
from .models import Like
from apps.posts.models import Post
from apps.comments.models import Comment


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_post_like(request, pk):
    try:
        post = Post.objects.get(pk=pk, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=404)

    like, created = Like.objects.get_or_create(
        user=request.user, target_type='post', target_id=pk,
    )
    if not created:
        like.delete()
        Post.objects.filter(pk=pk).update(like_count=F('like_count') - 1)
        return APIResponse(data={'is_liked': False, 'like_count': post.like_count - 1}, message='取消点赞')
    else:
        Post.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
        return APIResponse(data={'is_liked': True, 'like_count': post.like_count + 1}, message='点赞成功')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_comment_like(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        return APIResponse(code=404, message='评论不存在', status_code=404)

    like, created = Like.objects.get_or_create(
        user=request.user, target_type='comment', target_id=pk,
    )
    if not created:
        like.delete()
        Comment.objects.filter(pk=pk).update(like_count=F('like_count') - 1)
        return APIResponse(data={'is_liked': False, 'like_count': comment.like_count - 1}, message='取消点赞')
    else:
        Comment.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
        return APIResponse(data={'is_liked': True, 'like_count': comment.like_count + 1}, message='点赞成功')
