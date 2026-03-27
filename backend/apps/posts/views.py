from datetime import timedelta
from io import BytesIO

from django.db.models import Count, Q
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from PIL import Image

from apps.comments.models import Comment
from apps.interactions.models import Notification
from common.exceptions import APIResponse
from common.pagination import StandardPagination
from common.permissions import IsVerifiedUser
from apps.moderation.services import check_content

from .models import Announcement, Poll, PollOption, PollVote, Post, PostImage
from .recommendation import build_tag_scores, score_post
from .serializers import (
    AnnouncementSerializer,
    CreatePostSerializer,
    PostDetailSerializer,
    PostListSerializer,
)


def _apply_filters(queryset, request):
    search = request.query_params.get('search', '').strip()
    if search:
        queryset = queryset.filter(content__icontains=search)

    tag = request.query_params.get('tag')
    if tag:
        queryset = queryset.filter(tag=tag)

    time_filter = request.query_params.get('time')
    if time_filter == 'today':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=1))
    elif time_filter == 'week':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
    elif time_filter == 'month':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))

    return queryset


def _apply_expiration_side_effects():
    now = timezone.now()
    overdue_review_posts = Post.objects.filter(
        is_deleted=False,
        status='ai_suspect',
        review_deadline__isnull=False,
        review_deadline__lt=now,
    )
    for post in overdue_review_posts:
        post.status = 'rejected'
        post.moderation_source = 'manual'
        post.moderation_reason = post.moderation_reason or '管理员未在审核时限内处理，系统自动下架'
        post.reviewed_at = now
        post.save(update_fields=['status', 'moderation_source', 'moderation_reason', 'reviewed_at'])
        _notify_author(post.author, '你的帖子因超时未审核已自动下架', post.moderation_reason)

    expiring_posts = Post.objects.filter(
        is_deleted=False,
        destroy_after_hours__isnull=False,
        created_at__lt=now - timedelta(hours=1),
    )
    for post in expiring_posts:
        if post.is_expired:
            post.is_deleted = True
            post.save(update_fields=['is_deleted'])

    Post.objects.filter(is_pinned=True, pinned_until__lt=now).update(is_pinned=False)


def _exclude_expired_posts(posts):
    if isinstance(posts, list):
        return [post for post in posts if not post.is_expired]
    return [post for post in posts if not post.is_expired]


def _save_post_images(post, files):
    for uploaded in files[:3]:
        image = Image.open(uploaded)
        image = image.convert('RGB')

        original_buffer = BytesIO()
        image.save(original_buffer, format='JPEG', quality=85, optimize=True)
        original_content = ContentFile(original_buffer.getvalue(), name=f'post-{post.id}-{uploaded.name.rsplit(".", 1)[0]}.jpg')

        thumb = image.copy()
        thumb.thumbnail((480, 480))
        thumb_buffer = BytesIO()
        thumb.save(thumb_buffer, format='JPEG', quality=78, optimize=True)
        thumb_content = ContentFile(thumb_buffer.getvalue(), name=f'post-{post.id}-thumb-{uploaded.name.rsplit(".", 1)[0]}.jpg')

        PostImage.objects.create(post=post, image=original_content, thumbnail=thumb_content)


def _save_poll(post, request):
    poll_enabled = str(request.data.get('poll_enabled', '')).lower() in {'true', '1'}
    if not poll_enabled:
        return
    raw_options = request.data.getlist('poll_options') if hasattr(request.data, 'getlist') else []
    options = [option.strip() for option in raw_options if option.strip()]
    if len(options) < 2 or len(options) > 6:
        return
    expire_days = int(request.data.get('poll_expire_days', 3) or 3)
    poll = Poll.objects.create(
        post=post,
        question=request.data.get('poll_question', '').strip(),
        expire_days=expire_days,
    )
    for option in options:
        PollOption.objects.create(poll=poll, text=option[:30])


def _notify_admins(title, content, link='/admin/workbench/review-queue/'):
    from apps.users.models import User

    notifications = [
        Notification(
            user=admin,
            type='system',
            title=title[:120],
            content=content[:300],
            link=link,
        )
        for admin in User.objects.filter(is_staff=True, is_active=True)
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)


def _notify_author(author, title, content, link='/profile'):
    Notification.objects.create(
        user=author,
        type='system',
        title=title[:120],
        content=content[:300],
        link=link,
    )


def _resolve_post_audit_fields(audit):
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


def _recommend_posts(queryset, request):
    if not request.user.is_authenticated:
        return list(
            queryset.extra(
                select={'hot_score': 'like_count * 2 + comment_count * 3 + favorite_count * 1'},
            ).order_by('-hot_score', '-created_at')
        )

    posts = list(queryset)
    now = timezone.now()
    tag_scores = build_tag_scores(request.user)
    posts.sort(key=lambda post: score_post(post, tag_scores, now=now)['total'], reverse=True)
    return posts


@api_view(['GET'])
@permission_classes([AllowAny])
def post_list(request):
    _apply_expiration_side_effects()
    queryset = Post.objects.filter(
        is_deleted=False,
        status__in=['normal', 'ai_suspect'],
    ).select_related('identity').prefetch_related('images')

    queryset = _apply_filters(queryset, request)

    sort = request.query_params.get('sort', 'latest')
    if sort == 'hot':
        queryset = queryset.extra(
            select={'hot_score': 'like_count * 2 + comment_count * 3 + favorite_count * 1'},
        ).order_by('-is_pinned', '-hot_score', '-created_at')
    elif sort == 'recommend':
        queryset = _recommend_posts(queryset, request)
    else:
        queryset = queryset.order_by('-is_pinned', '-created_at')

    paginator = StandardPagination()
    page = paginator.paginate_queryset(_exclude_expired_posts(queryset), request)
    serializer = PostListSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def home_meta(request):
    _apply_expiration_side_effects()
    now = timezone.now()
    announcements = (
        Announcement.objects.filter(is_active=True)
        .filter(Q(start_at__lte=now) | Q(start_at__isnull=True))
        .filter(Q(end_at__gte=now) | Q(end_at__isnull=True))
        .order_by('-created_at')[:3]
    )

    pinned_posts = Post.objects.filter(
        is_deleted=False,
        status__in=['normal', 'ai_suspect'],
        is_pinned=True,
    ).select_related('identity').prefetch_related('images')
    pinned_posts = _exclude_expired_posts(pinned_posts.exclude(pinned_until__lt=now).order_by('-created_at')[:3])

    return APIResponse(
        data={
            'announcements': AnnouncementSerializer(announcements, many=True).data,
            'pinned_posts': PostListSerializer(pinned_posts, many=True, context={'request': request}).data,
        }
    )


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def create_post(request):
    serializer = CreatePostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    content = serializer.validated_data['content']
    audit = check_content(content, content_type='post')
    identity = request.user.identities.order_by('-created_at').first()
    audit_fields = _resolve_post_audit_fields(audit)
    post = serializer.save(
        author=request.user,
        identity=identity,
        **audit_fields,
    )
    _save_post_images(post, request.FILES.getlist('images'))
    _save_poll(post, request)

    if post.status == 'rejected':
        _notify_author(
            request.user,
            '你的帖子因违规已被下架',
            post.moderation_reason or post.ai_reason or '内容不符合社区规范',
        )
        return APIResponse(
            data=PostDetailSerializer(post, context={'request': request}).data,
            message='内容违规，已自动下架。你可以在个人主页查看违规原因。',
            status_code=status.HTTP_201_CREATED,
        )

    if post.status == 'ai_suspect':
        _notify_admins(
            '有新的帖子需要审核',
            f'帖子 #{post.id} 进入审核队列：{post.moderation_reason or post.ai_reason}',
        )

    return APIResponse(
        data=PostDetailSerializer(post, context={'request': request}).data,
        message='发布成功' if post.status == 'normal' else '内容已上架，并已通知管理员审核',
        status_code=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def post_detail(request, pk):
    _apply_expiration_side_effects()
    try:
        post = Post.objects.select_related('identity').prefetch_related('images', 'poll__options').get(pk=pk, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)
    if post.is_expired:
        return APIResponse(code=404, message='帖子已自毁', status_code=status.HTTP_404_NOT_FOUND)
    if post.status in {'pending', 'rejected'}:
        is_owner = bool(request.user.is_authenticated and (request.user.id == post.author_id or request.user.is_staff))
        if not is_owner:
            return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)

    serializer = PostDetailSerializer(post, context={'request': request})
    return APIResponse(data=serializer.data)


@api_view(['PATCH'])
@permission_classes([IsVerifiedUser])
def update_post(request, pk):
    try:
        post = Post.objects.get(pk=pk, author=request.user, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)
    if timezone.now() - post.created_at > timedelta(minutes=10):
        return APIResponse(code=400, message='仅支持发布后 10 分钟内编辑', status_code=status.HTTP_400_BAD_REQUEST)

    content = request.data.get('content', post.content)
    if not content.strip():
        return APIResponse(code=400, message='内容不能为空', status_code=status.HTTP_400_BAD_REQUEST)
    if len(content) > 500:
        return APIResponse(code=400, message='内容不能超过 500 字', status_code=status.HTTP_400_BAD_REQUEST)

    audit = check_content(content, content_type='post')
    post.content = content
    post.bg_color = int(request.data.get('bg_color', post.bg_color))
    post.allow_messages = str(request.data.get('allow_messages', post.allow_messages)).lower() in {'true', '1'} if 'allow_messages' in request.data else post.allow_messages
    for key, value in _resolve_post_audit_fields(audit).items():
        setattr(post, key, value)
    post.save()

    if request.data.get('replace_images') == 'true':
        post.images.all().delete()
        _save_post_images(post, request.FILES.getlist('images'))

    if post.status == 'rejected':
        _notify_author(
            request.user,
            '你修改后的帖子因违规已被下架',
            post.moderation_reason or post.ai_reason or '内容不符合社区规范',
        )
    elif post.status == 'ai_suspect':
        _notify_admins(
            '有帖子修改后需要复核',
            f'帖子 #{post.id} 进入审核队列：{post.moderation_reason or post.ai_reason}',
        )

    return APIResponse(
        data=PostDetailSerializer(post, context={'request': request}).data,
        message='编辑成功' if post.status == 'normal' else '修改已保存，并进入审核流程',
    )


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def vote_poll(request, pk):
    try:
        post = Post.objects.select_related('poll').get(pk=pk, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)
    if not hasattr(post, 'poll'):
        return APIResponse(code=400, message='该帖子没有投票', status_code=status.HTTP_400_BAD_REQUEST)

    poll = post.poll
    if poll.created_at + timedelta(days=poll.expire_days) <= timezone.now():
        return APIResponse(code=400, message='投票已截止', status_code=status.HTTP_400_BAD_REQUEST)
    if PollVote.objects.filter(poll=poll, user=request.user).exists():
        return APIResponse(code=400, message='你已经投过票了', status_code=status.HTTP_400_BAD_REQUEST)

    option_id = request.data.get('option_id')
    try:
        option = poll.options.get(pk=option_id)
    except PollOption.DoesNotExist:
        return APIResponse(code=400, message='投票选项不存在', status_code=status.HTTP_400_BAD_REQUEST)

    PollVote.objects.create(poll=poll, option=option, user=request.user)
    option.vote_count = F('vote_count') + 1
    option.save(update_fields=['vote_count'])
    option.refresh_from_db()
    return APIResponse(data=PostDetailSerializer(post, context={'request': request}).data, message='投票成功')


@api_view(['DELETE'])
@permission_classes([IsVerifiedUser])
def delete_post(request, pk):
    try:
        post = Post.objects.get(pk=pk, author=request.user, is_deleted=False)
    except Post.DoesNotExist:
        return APIResponse(code=404, message='帖子不存在', status_code=status.HTTP_404_NOT_FOUND)

    post.is_deleted = True
    post.save(update_fields=['is_deleted'])
    return APIResponse(message='删除成功')
