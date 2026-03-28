from datetime import timedelta

from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone

from apps.posts.recommendation import get_recommendation_snapshot
from apps.users.models import User
from apps.interactions.models import Notification, Report
from apps.moderation.models import AuditLog
from common.unread_cache import invalidate_notification_unread

from .admin_panel import (
    WORKBENCH_URLS,
    get_admin_metrics,
    get_moderation_detail_snapshot,
    get_admin_trends,
    get_content_center_snapshot,
    get_operations_center,
    get_report_queue,
    get_review_queue,
    get_user_detail_snapshot,
    get_user_center,
    get_workbench_navigation,
    get_workbench_page_pills,
)


def build_workbench_context(request, active_key, title, intro, metrics=None, actions=None):
    current_metrics = metrics or get_admin_metrics()
    return {
        **admin.site.each_context(request),
        'title': title,
        'metrics': current_metrics,
        'wb_page_title': title,
        'wb_page_intro': intro,
        'wb_page_pills': get_workbench_page_pills(current_metrics),
        'wb_page_actions': actions or [],
        'wb_nav_sections': get_workbench_navigation(active_key, current_metrics),
    }


def content_center_view(request):
    metrics = get_admin_metrics()

    kind = request.GET.get('kind', 'post')
    status = request.GET.get('status', '').strip()
    search = request.GET.get('search', '').strip()

    snapshot = get_content_center_snapshot(kind=kind, status=status, search=search, limit=12)
    context = {
        **build_workbench_context(
            request,
            'content_center',
            '内容中心',
            '用同一套筛选与状态汇总查看帖子或评论，减少帖子、评论、审核页之间来回切换。',
            metrics=metrics,
            actions=[
                {'label': '去审核队列', 'url': WORKBENCH_URLS['review_queue'], 'tone': 'primary'},
                {'label': '去举报中心', 'url': WORKBENCH_URLS['report_center'], 'tone': 'ghost'},
            ],
        ),
        'kind': kind,
        'status': status,
        'search': search,
        **snapshot,
    }
    return TemplateResponse(request, 'admin/workbench/content_center.html', context)


def dashboard_view(request):
    metrics = get_admin_metrics()
    context = {
        **build_workbench_context(
            request,
            'dashboard',
            '后台总览',
            '先看今日整体态势，再决定是进入审核、举报、内容还是用户工作流。',
            metrics=metrics,
            actions=[
                {'label': '处理审核任务', 'url': WORKBENCH_URLS['review_queue'], 'tone': 'primary'},
                {'label': '查看举报', 'url': WORKBENCH_URLS['report_center'], 'tone': 'ghost'},
            ],
        ),
        'trends': get_admin_trends(7),
        'queue_rows': get_review_queue(8),
        'report_rows': get_report_queue(8),
    }
    return TemplateResponse(request, 'admin/workbench/dashboard.html', context)


def review_queue_view(request):
    metrics = get_admin_metrics()
    context = {
        **build_workbench_context(
            request,
            'review_queue',
            '审核队列',
            '把举报、待审核和 AI 存疑内容放进同一条人工处理流水线，先处理风险最高的项。',
            metrics=metrics,
            actions=[
                {'label': '去举报中心', 'url': WORKBENCH_URLS['report_center'], 'tone': 'primary'},
                {'label': '去内容中心', 'url': WORKBENCH_URLS['content_center'], 'tone': 'ghost'},
            ],
        ),
        'queue_rows': get_review_queue(20),
        'trends': get_admin_trends(7),
    }
    return TemplateResponse(request, 'admin/workbench/review_queue.html', context)


def report_center_view(request):
    metrics = get_admin_metrics()
    context = {
        **build_workbench_context(
            request,
            'report_center',
            '举报中心',
            '集中处理用户举报，并快速回到目标内容、作者和最终处罚动作。',
            metrics=metrics,
            actions=[
                {'label': '去审核队列', 'url': WORKBENCH_URLS['review_queue'], 'tone': 'primary'},
                {'label': '查看用户中心', 'url': WORKBENCH_URLS['user_center'], 'tone': 'ghost'},
            ],
        ),
        'report_rows': get_report_queue(20),
    }
    return TemplateResponse(request, 'admin/workbench/report_center.html', context)


def user_center_view(request):
    metrics = get_admin_metrics()
    context = {
        **build_workbench_context(
            request,
            'user_center',
            '用户中心',
            '从待认证、禁言中和高风险用户三个角度追踪账号状态，辅助审核与处罚决策。',
            metrics=metrics,
            actions=[
                {'label': '去审核队列', 'url': WORKBENCH_URLS['review_queue'], 'tone': 'primary'},
            ],
        ),
        **get_user_center(10),
    }
    return TemplateResponse(request, 'admin/workbench/user_center.html', context)


def user_detail_view(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect(WORKBENCH_URLS['user_center'])

    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', '').strip()

        if action == 'verify':
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            AuditLog.objects.create(
                auditor=request.user,
                target_type='user',
                target_id=user.id,
                action='approve',
                reason=reason or '管理员通过了用户认证',
            )
            return redirect(request.path)

        if action in {'ban_7', 'ban_30', 'ban_forever'}:
            days = None if action == 'ban_forever' else (7 if action == 'ban_7' else 30)
            user.is_banned = True
            user.ban_until = None if days is None else timezone.now() + timedelta(days=days)
            user.save(update_fields=['is_banned', 'ban_until'])
            AuditLog.objects.create(
                auditor=request.user,
                target_type='user',
                target_id=user.id,
                action='ban',
                reason=reason or (f'管理员禁言 {days} 天' if days else '管理员永久禁言'),
            )
            return redirect(request.path)

        if action == 'unban':
            user.is_banned = False
            user.ban_until = None
            user.save(update_fields=['is_banned', 'ban_until'])
            AuditLog.objects.create(
                auditor=request.user,
                target_type='user',
                target_id=user.id,
                action='approve',
                reason=reason or '管理员解除禁言',
            )
            return redirect(request.path)

    metrics = get_admin_metrics()
    context = {
        **build_workbench_context(
            request,
            'user_center',
            f'用户中心 · {user.email}',
            '围绕单个用户查看内容记录、通知与违规历史，并直接完成认证、禁言与解禁处理。',
            metrics=metrics,
            actions=[
                {'label': '返回用户中心', 'url': WORKBENCH_URLS['user_center'], 'tone': 'primary'},
            ],
        ),
        **get_user_detail_snapshot(user),
    }
    return TemplateResponse(request, 'admin/workbench/user_detail.html', context)


def operations_center_view(request):
    metrics = get_admin_metrics()
    context = {
        **build_workbench_context(
            request,
            'operations_center',
            '运营配置',
            '把敏感词、公告、置顶和审核留痕放在同一个运营视角下统一查看。',
            metrics=metrics,
            actions=[
                {'label': '管理敏感词', 'url': '/admin/moderation/sensitiveword/', 'tone': 'primary'},
                {'label': '管理公告', 'url': '/admin/posts/announcement/', 'tone': 'ghost'},
            ],
        ),
        **get_operations_center(10),
    }
    return TemplateResponse(request, 'admin/workbench/operations_center.html', context)


def recommendation_center_view(request):
    users = list(User.objects.filter(is_staff=False).order_by('-date_joined')[:50])
    selected_user = None
    selected_id = request.GET.get('user_id')
    if selected_id:
        selected_user = next((user for user in users if str(user.id) == str(selected_id)), None)
    if not selected_user and users:
        selected_user = users[0]

    metrics = get_admin_metrics()
    context = {
        **build_workbench_context(
            request,
            'recommendation_center',
            '推荐系统',
            '把推荐公式、用户兴趣标签和结果拆解放到同一个解释视图里，方便核对推荐逻辑。',
            metrics=metrics,
            actions=[
                {'label': '回到后台总览', 'url': WORKBENCH_URLS['dashboard'], 'tone': 'primary'},
                {'label': '查看用户中心', 'url': WORKBENCH_URLS['user_center'], 'tone': 'ghost'},
            ],
        ),
        'users': users,
        'snapshot': get_recommendation_snapshot(selected_user, limit=12) if selected_user else None,
    }
    return TemplateResponse(request, 'admin/workbench/recommendation_center.html', context)


def _finalize_target_action(target, action, request, reason):
    now = timezone.now()
    target_type = 'post' if target.__class__.__name__ == 'Post' else 'comment'
    target.status = 'normal' if action == 'approve' else 'rejected'
    if hasattr(target, 'moderation_source'):
        target.moderation_source = 'manual'
    if hasattr(target, 'moderation_reason'):
        target.moderation_reason = reason
    if hasattr(target, 'review_deadline'):
        target.review_deadline = None
    if hasattr(target, 'reviewed_at'):
        target.reviewed_at = now
    update_fields = ['status']
    for field in ('moderation_source', 'moderation_reason', 'review_deadline', 'reviewed_at'):
        if hasattr(target, field):
            update_fields.append(field)
    target.save(update_fields=update_fields)

    AuditLog.objects.create(
        auditor=request.user,
        target_type=target_type,
        target_id=target.id,
        action='approve' if action == 'approve' else 'reject',
        reason=reason,
    )

    Notification.objects.create(
        user=target.author,
        type='system',
        title='你的内容已通过管理员审核' if action == 'approve' else '你的内容已被管理员下架',
        content=reason,
        link='/profile',
    )
    invalidate_notification_unread(target.author_id)

    pending_reports = list(Report.objects.filter(target_type=target_type, target_id=target.id, status='pending').select_related('user'))
    Report.objects.filter(
        target_type=target_type,
        target_id=target.id,
        status='pending',
    ).update(status='resolved')
    if pending_reports:
        Notification.objects.bulk_create([
            Notification(
                user=report.user,
                type='report',
                title='你举报的内容已处理',
                content=reason,
                link='/messages?tab=notifications',
            )
            for report in pending_reports
        ])
        for report in pending_reports:
            invalidate_notification_unread(report.user_id)


def moderation_detail_view(request, target_type, target_id):
    snapshot = get_moderation_detail_snapshot(target_type, target_id)
    if snapshot is None:
        return redirect(WORKBENCH_URLS['review_queue'])

    target = snapshot['target']
    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', '').strip()

        if action == 'approve':
            _finalize_target_action(target, 'approve', request, reason or '管理员审核通过')
            return redirect(request.path)

        if action == 'reject':
            _finalize_target_action(target, 'reject', request, reason or '管理员下架内容')
            return redirect(request.path)

        if action in {'ban_7', 'ban_30', 'ban_forever'}:
            days = None if action == 'ban_forever' else (7 if action == 'ban_7' else 30)
            target.author.is_banned = True
            target.author.ban_until = None if days is None else timezone.now() + timedelta(days=days)
            target.author.save(update_fields=['is_banned', 'ban_until'])
            _finalize_target_action(
                target,
                'reject',
                request,
                reason or (f'管理员下架内容并禁言 {days} 天' if days else '管理员下架内容并永久禁言'),
            )
            AuditLog.objects.create(
                auditor=request.user,
                target_type='user',
                target_id=target.author_id,
                action='ban',
                reason=reason or (f'管理员禁言 {days} 天' if days else '管理员永久禁言'),
            )
            return redirect(request.path)

        if action == 'ignore_report':
            report_id = request.POST.get('report_id')
            Report.objects.filter(pk=report_id, target_type=target_type, target_id=target_id, status='pending').update(status='ignored')
            return redirect(request.path)

        if action == 'ignore_all_reports':
            Report.objects.filter(target_type=target_type, target_id=target_id, status='pending').update(status='ignored')
            return redirect(request.path)

    context = {
        **build_workbench_context(
            request,
            'review_queue',
            f'审核详情 · {"帖子" if target_type == "post" else "评论"} #{target_id}',
            '围绕单条内容完成审核决策、举报处理与用户处罚，不再跳转回原始表单。',
            actions=[
                {'label': '返回审核队列', 'url': WORKBENCH_URLS['review_queue'], 'tone': 'primary'},
                {'label': '去举报中心', 'url': WORKBENCH_URLS['report_center'], 'tone': 'ghost'},
            ],
        ),
        **snapshot,
    }
    return TemplateResponse(request, 'admin/workbench/moderation_detail.html', context)
