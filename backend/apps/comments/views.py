from datetime import timedelta

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from common.permissions import IsVerifiedUser
from django.db.models import F
from django.utils import timezone
from common.exceptions import APIResponse
from common.pagination import StandardPagination
from common.unread_cache import invalidate_notification_unread
from .models import Comment
from .serializers import CommentSerializer, CreateCommentSerializer
from apps.posts.models import Post
from apps.interactions.models import Notification


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


def _notify_admins(title, content, link='/admin/workbench/review-queue/'):
    from apps.users.models import User

    admins = list(User.objects.filter(is_staff=True, is_active=True))
    notifications = [
        Notification(
            user=admin,
            type='system',
            title=title[:120],
            content=content[:300],
            link=link,
        )
        for admin in admins
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)
        for admin in admins:
            invalidate_notification_unread(admin.id)


def _notify_author(author, title, content, link='/profile'):
    Notification.objects.create(
        user=author,
        type='system',
        title=title[:120],
        content=content[:300],
        link=link,
    )
    invalidate_notification_unread(author.id)


def _resolve_comment_audit_fields(audit):
    now = timezone.now()
    fields = {
        'status': 'normal',
        'moderation_source': audit.get('moderation_source', 'none'),
        'moderation_reason': audit.get('moderation_reason', ''),
        'ai_decision': audit.get('ai_decision', ''),
        'ai_reason': audit.get('ai_reason', ''),
        'risk_level': audit.get('ai_risk_level', 'none'),
        'review_deadline': None,
        'reviewed_at': now,
    }

    if audit['moderation_source'] == 'hard_word':
        fields.update({'status': 'rejected', 'risk_level': 'high'})
        return fields

    if audit['moderation_source'] == 'soft_word':
        fields.update({
            'status': 'ai_suspect',
            'risk_level': 'medium',
            'review_deadline': now + timedelta(days=7),
            'reviewed_at': None,
        })
        return fields

    if audit['ai_decision'] == 'reject':
        fields.update({'status': 'rejected', 'risk_level': 'high'})
        return fields

    if audit['ai_decision'] == 'confuse':
        deadline = None
        if audit['ai_risk_level'] == 'high':
            deadline = now + timedelta(days=3)
        elif audit['ai_risk_level'] == 'medium':
            deadline = now + timedelta(days=7)
        fields.update({
            'status': 'ai_suspect',
            'review_deadline': deadline,
            'reviewed_at': None,
        })
        return fields

    return fields


def _apply_comment_review_side_effects(post):
    now = timezone.now()
    overdue_comments = Comment.objects.filter(
        post=post,
        status='ai_suspect',
        review_deadline__isnull=False,
        review_deadline__lt=now,
    ).select_related('author')
    for comment in overdue_comments:
        comment.status = 'rejected'
        comment.moderation_source = 'manual'
        comment.moderation_reason = comment.moderation_reason or '管理员未在审核时限内处理，系统自动下架'
        comment.reviewed_at = now
        comment.save(update_fields=['status', 'moderation_source', 'moderation_reason', 'reviewed_at'])
        _notify_author(comment.author, '你的评论因超时未审核已自动下架', comment.moderation_reason)


@api_view(['GET'])
@permission_classes([AllowAny])
def comment_list(request, post_id):
    try:
        post = Post.objects.get(pk=post_id, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)
    if post.is_expired:
        return APIResponse(code=404, message='帖子已自毁', status_code=status.HTTP_404_NOT_FOUND)
    _apply_comment_review_side_effects(post)

    queryset = Comment.objects.filter(
        post=post, status__in=['normal', 'ai_suspect']
    ).select_related('parent', 'identity', 'parent__identity').order_by('created_at')

    user_map = _build_user_map(post_id)

    paginator = StandardPagination()
    paginator.page_size = 200  # Large page to keep comment tree intact
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
@permission_classes([IsVerifiedUser])
def create_comment(request, post_id):
    try:
        post = Post.objects.get(pk=post_id, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)
    if post.is_expired:
        return APIResponse(code=404, message='帖子已自毁', status_code=status.HTTP_404_NOT_FOUND)
    _apply_comment_review_side_effects(post)

    serializer = CreateCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    from apps.moderation.services import check_content
    content = serializer.validated_data['content']
    audit = check_content(content, content_type='comment')

    parent = None
    parent_id = serializer.validated_data.get('parent_id')
    if parent_id:
        try:
            parent = Comment.objects.get(pk=parent_id, post=post)
        except Comment.DoesNotExist:
            return APIResponse(code=400, message='回复的评论不存在', status_code=status.HTTP_400_BAD_REQUEST)

    duplicate_exists = Comment.objects.filter(
        post=post,
        author=request.user,
        parent=parent,
        content=serializer.validated_data['content'],
        created_at__gte=timezone.now() - timedelta(seconds=8),
    ).exists()
    if duplicate_exists:
        return APIResponse(code=400, message='检测到重复评论，请不要连续重复提交', status_code=status.HTTP_400_BAD_REQUEST)

    identity = request.user.identities.order_by('-created_at').first()
    audit_fields = _resolve_comment_audit_fields(audit)
    comment = Comment.objects.create(
        post=post,
        author=request.user,
        identity=identity,
        parent=parent,
        content=serializer.validated_data['content'],
        **audit_fields,
    )
    if comment.status != 'rejected':
        Post.objects.filter(pk=post_id).update(comment_count=F('comment_count') + 1)
    if post.author_id != request.user.id:
        Notification.objects.create(
            user=post.author,
            type='comment',
            title='有人评论了你的帖子',
            content=serializer.validated_data['content'][:300],
            link=f'/post/{post.id}#comments',
        )
        invalidate_notification_unread(post.author_id)

    user_map = _build_user_map(post_id)
    result = CommentSerializer(
        comment,
        context={
            'request': request,
            'user_map': user_map,
            'post_author_id': post.author_id,
        }
    ).data
    if comment.status == 'rejected':
        _notify_author(
            request.user,
            '你的评论因违规已被下架',
            comment.moderation_reason or comment.ai_reason or '内容不符合社区规范',
        )
    elif comment.status == 'ai_suspect':
        _notify_admins(
            '有新的评论需要审核',
            f'评论 #{comment.id} 进入审核队列：{comment.moderation_reason or comment.ai_reason}',
        )
    return APIResponse(
        data=result,
        message='评论成功' if comment.status == 'normal' else ('评论违规，已自动下架。你可以在个人主页查看原因。' if comment.status == 'rejected' else '评论已上架，并已通知管理员审核'),
        status_code=status.HTTP_201_CREATED,
    )


@api_view(['DELETE'])
@permission_classes([IsVerifiedUser])
def delete_comment(request, pk):
    try:
        comment = Comment.objects.get(pk=pk, author=request.user)
    except Comment.DoesNotExist:
        return APIResponse(code=404, message='评论不存在', status_code=status.HTTP_404_NOT_FOUND)
    post_id = comment.post_id
    comment.delete()
    Post.objects.filter(pk=post_id).update(comment_count=F('comment_count') - 1)
    return APIResponse(message='删除成功')
