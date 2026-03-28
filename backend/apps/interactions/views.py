from datetime import timedelta

from django.db.models import F, Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.comments.models import Comment
from apps.posts.models import Post
from common.exceptions import APIResponse
from common.permissions import IsVerifiedUser
from common.unread_cache import (
    get_unread_summary,
    invalidate_message_unread,
    invalidate_notification_unread,
    set_message_unread_count,
    set_notification_unread_count,
)

from .models import Conversation, Favorite, Like, Notification, PrivateMessage, Report
from .serializers import ConversationSerializer, NotificationSerializer


class ReportSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(choices=Report.TARGET_CHOICES)
    target_id = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=Report.REASON_CHOICES)
    detail = serializers.CharField(max_length=100, required=False, allow_blank=True)


class MessageCreateSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    content = serializers.CharField(max_length=300)


class MessageReplySerializer(serializers.Serializer):
    content = serializers.CharField(max_length=300)


def _get_post(pk):
    try:
        post = Post.objects.get(pk=pk, is_deleted=False)
    except Post.DoesNotExist:
        return None
    if post.is_expired:
        return None
    return post


def _get_comment(pk):
    try:
        return Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        return None


def _create_notification(user, type_, title, content, link=''):
    Notification.objects.create(
        user=user,
        type=type_,
        title=title[:120],
        content=content[:300],
        link=link,
    )
    if type_ == 'message':
        invalidate_message_unread(user.id)
    else:
        invalidate_notification_unread(user.id)


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def toggle_post_like(request, pk):
    post = _get_post(pk)
    if post is None:
        return APIResponse(code=404, message='帖子不存在', status_code=404)

    like, created = Like.objects.get_or_create(user=request.user, target_type='post', target_id=pk)
    if created:
        Post.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
        if post.author_id != request.user.id:
            _create_notification(
                user=post.author,
                type_='like',
                title='你的帖子收到了新的点赞',
                content=f'你的「{post.tag}」帖子收到了一次点赞。',
                link=f'/post/{post.id}',
            )
        return APIResponse(data={'is_liked': True, 'like_count': post.like_count + 1}, message='点赞成功')

    like.delete()
    Post.objects.filter(pk=pk).update(like_count=F('like_count') - 1)
    return APIResponse(data={'is_liked': False, 'like_count': max(post.like_count - 1, 0)}, message='取消点赞')


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def toggle_comment_like(request, pk):
    comment = _get_comment(pk)
    if comment is None:
        return APIResponse(code=404, message='评论不存在', status_code=404)

    like, created = Like.objects.get_or_create(user=request.user, target_type='comment', target_id=pk)
    if created:
        Comment.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
        if comment.author_id != request.user.id:
            _create_notification(
                user=comment.author,
                type_='like',
                title='你的评论收到了新的点赞',
                content='有人点赞了你在帖子下的评论。',
                link=f'/post/{comment.post_id}#comments',
            )
        return APIResponse(data={'is_liked': True, 'like_count': comment.like_count + 1}, message='点赞成功')

    like.delete()
    Comment.objects.filter(pk=pk).update(like_count=F('like_count') - 1)
    return APIResponse(data={'is_liked': False, 'like_count': max(comment.like_count - 1, 0)}, message='取消点赞')


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def toggle_post_favorite(request, pk):
    post = _get_post(pk)
    if post is None:
        return APIResponse(code=404, message='帖子不存在', status_code=404)

    favorite, created = Favorite.objects.get_or_create(user=request.user, target_type='post', target_id=pk)
    if created:
        Post.objects.filter(pk=pk).update(favorite_count=F('favorite_count') + 1)
        if post.author_id != request.user.id:
            _create_notification(
                user=post.author,
                type_='favorite',
                title='你的帖子被收藏了',
                content=f'你的「{post.tag}」帖子被加入收藏列表。',
                link=f'/post/{post.id}',
            )
        return APIResponse(data={'is_favorited': True, 'favorite_count': post.favorite_count + 1}, message='收藏成功')

    favorite.delete()
    Post.objects.filter(pk=pk).update(favorite_count=F('favorite_count') - 1)
    return APIResponse(data={'is_favorited': False, 'favorite_count': max(post.favorite_count - 1, 0)}, message='已取消收藏')


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def create_report(request):
    serializer = ReportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    target_type = serializer.validated_data['target_type']
    target_id = serializer.validated_data['target_id']

    if target_type == 'post':
        target = _get_post(target_id)
    else:
        target = _get_comment(target_id)
    if target is None:
        return APIResponse(code=404, message='举报目标不存在', status_code=404)

    report, created = Report.objects.get_or_create(
        user=request.user,
        target_type=target_type,
        target_id=target_id,
        defaults={'reason': serializer.validated_data['reason'], 'detail': serializer.validated_data.get('detail', '')},
    )
    if not created:
        return APIResponse(code=400, message='你已经举报过这条内容', status_code=400)

    owner = getattr(target, 'author', None)
    if owner and owner != request.user:
        _create_notification(
            user=owner,
            type_='report',
            title='你的内容被举报',
            content=f'原因：{report.reason}',
            link=f'/post/{target.post_id if target_type == "comment" else target.id}',
        )

    return APIResponse(message='举报已提交，感谢你的反馈')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    queryset = request.user.notifications.order_by('-created_at')[:100]
    return APIResponse(data=NotificationSerializer(queryset, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_summary(request):
    return APIResponse(data=get_unread_summary(request.user))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True, is_ignored=False)
    set_notification_unread_count(request.user.id, 0)
    return APIResponse(message='已全部标记为已读')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notification = request.user.notifications.get(pk=pk)
    except Notification.DoesNotExist:
        return APIResponse(code=404, message='通知不存在', status_code=404)
    notification.is_read = True
    notification.is_ignored = False
    notification.save(update_fields=['is_read', 'is_ignored'])
    set_notification_unread_count(
        request.user.id,
        request.user.notifications.filter(is_read=False).count(),
    )
    return APIResponse(message='已标记为已读')


@api_view(['GET'])
@permission_classes([IsVerifiedUser])
def conversation_list(request):
    user_conversations = Conversation.objects.filter(
        Q(owner=request.user) | Q(participant=request.user)
    )
    PrivateMessage.objects.filter(
        pk__in=PrivateMessage.objects.filter(
            conversation__in=user_conversations,
            is_read=False,
        ).exclude(sender=request.user).values('pk')
    ).update(is_read=True)
    set_message_unread_count(request.user.id, 0)
    queryset = user_conversations.select_related('post', 'owner', 'participant')
    serializer = ConversationSerializer(queryset, many=True, context={'request': request})
    unread_notifications = get_unread_summary(request.user)['notifications']
    return APIResponse(data={
        'conversations': serializer.data,
        'notification_unread_count': unread_notifications,
        'message_unread_count': 0,
    })


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def send_message(request):
    serializer = MessageCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    post = _get_post(serializer.validated_data['post_id'])
    if post is None:
        return APIResponse(code=404, message='帖子不存在', status_code=404)
    if not post.allow_messages:
        return APIResponse(code=400, message='该帖子未开启私信', status_code=400)
    if post.author_id == request.user.id:
        return APIResponse(code=400, message='不能给自己的帖子发私信', status_code=400)

    today = timezone.now() - timedelta(days=1)
    sent_today = PrivateMessage.objects.filter(
        sender=request.user,
        conversation__post=post,
        conversation__owner=post.author,
        created_at__gte=today,
    ).count()
    if sent_today >= 3:
        return APIResponse(code=400, message='对同一楼主每天最多发送 3 条私信', status_code=400)

    conversation, _ = Conversation.objects.get_or_create(
        post=post,
        owner=post.author,
        participant=request.user,
    )
    if conversation.is_blocked:
        return APIResponse(code=403, message='该会话已被楼主关闭', status_code=403)

    message = PrivateMessage.objects.create(
        conversation=conversation,
        sender=request.user,
        content=serializer.validated_data['content'],
    )
    conversation.save(update_fields=['updated_at'])
    _create_notification(
        user=post.author,
        type_='message',
        title='你收到了一条新的匿名私信',
        content=serializer.validated_data['content'],
        link=f'/messages?tab=messages&conversation={conversation.id}',
    )
    serializer = ConversationSerializer(conversation, context={'request': request})
    return APIResponse(data=serializer.data, message='私信发送成功')


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def reply_message(request, conversation_id):
    serializer = MessageReplySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        conversation = Conversation.objects.get(pk=conversation_id)
    except Conversation.DoesNotExist:
        return APIResponse(code=404, message='会话不存在', status_code=404)
    if request.user.id not in {conversation.owner_id, conversation.participant_id}:
        return APIResponse(code=403, message='无权访问该会话', status_code=403)
    if conversation.is_blocked and request.user.id == conversation.participant_id:
        return APIResponse(code=403, message='该会话已被楼主关闭', status_code=403)

    message = PrivateMessage.objects.create(conversation=conversation, sender=request.user, content=serializer.validated_data['content'])
    recipient = conversation.participant if request.user.id == conversation.owner_id else conversation.owner
    _create_notification(
        user=recipient,
        type_='message',
        title='你收到了一条新的匿名私信',
        content=message.content,
        link=f'/messages?tab=messages&conversation={conversation.id}',
    )
    conversation.save(update_fields=['updated_at'])
    return APIResponse(data=ConversationSerializer(conversation, context={'request': request}).data, message='发送成功')


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def block_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(pk=conversation_id, owner=request.user)
    except Conversation.DoesNotExist:
        return APIResponse(code=404, message='会话不存在', status_code=404)
    conversation.is_blocked = True
    conversation.save(update_fields=['is_blocked'])
    return APIResponse(message='会话已关闭')
