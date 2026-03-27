from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.comments.models import Comment
from apps.interactions.models import Notification, PrivateMessage, Report
from apps.moderation.models import AuditLog, SensitiveWord
from apps.posts.models import Announcement, Post
from apps.users.models import User


WORKBENCH_URLS = {
    'dashboard': '/admin/workbench/dashboard/',
    'review_queue': '/admin/workbench/review-queue/',
    'report_center': '/admin/workbench/reports/',
    'content_center': '/admin/workbench/content/',
    'user_center': '/admin/workbench/users/',
    'operations_center': '/admin/workbench/operations/',
    'recommendation_center': '/admin/workbench/recommendation/',
}


def content_preview(obj, length=64):
    content = getattr(obj, 'content', '') or ''
    return content if len(content) <= length else f'{content[:length]}...'


def get_admin_metrics():
    now = timezone.localtime()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_post_count = Post.objects.filter(created_at__gte=today_start).count()
    today_comment_count = Comment.objects.filter(created_at__gte=today_start).count()
    pending_post_count = Post.objects.filter(status='pending', is_deleted=False).count()
    pending_comment_count = Comment.objects.filter(status='pending').count()
    pending_reports_count = Report.objects.filter(status='pending').count()
    pending_verification_count = User.objects.filter(is_verified=False, is_staff=False).count()
    banned_user_count = User.objects.filter(is_banned=True).count()
    ai_suspect_count = (
        Post.objects.filter(status='ai_suspect', is_deleted=False).count()
        + Comment.objects.filter(status='ai_suspect').count()
    )
    pinned_post_count = Post.objects.filter(is_pinned=True, is_deleted=False).count()
    active_announcement_count = (
        Announcement.objects.filter(is_active=True)
        .filter(Q(start_at__lte=now) | Q(start_at__isnull=True))
        .filter(Q(end_at__gte=now) | Q(end_at__isnull=True))
        .count()
    )

    active_user_ids = set(Post.objects.filter(created_at__gte=today_start).values_list('author_id', flat=True))
    active_user_ids.update(Comment.objects.filter(created_at__gte=today_start).values_list('author_id', flat=True))
    active_user_ids.update(PrivateMessage.objects.filter(created_at__gte=today_start).values_list('sender_id', flat=True))

    return {
        'today_post_count': today_post_count,
        'today_comment_count': today_comment_count,
        'today_active_users': len(active_user_ids),
        'pending_content_count': pending_post_count + pending_comment_count,
        'pending_reports_count': pending_reports_count,
        'pending_verification_count': pending_verification_count,
        'banned_user_count': banned_user_count,
        'ai_suspect_count': ai_suspect_count,
        'pinned_post_count': pinned_post_count,
        'active_announcement_count': active_announcement_count,
    }


def get_workbench_page_pills(metrics):
    return [
        {
            'label': '待审核内容',
            'value': metrics['pending_content_count'],
            'tone': 'danger',
        },
        {
            'label': '待处理举报',
            'value': metrics['pending_reports_count'],
            'tone': 'warn',
        },
        {
            'label': '待认证用户',
            'value': metrics['pending_verification_count'],
            'tone': 'neutral',
        },
        {
            'label': '禁言中用户',
            'value': metrics['banned_user_count'],
            'tone': 'neutral',
        },
    ]


def get_workbench_navigation(active_key, metrics):
    return [
        {
            'title': '工作流主线',
            'items': [
                {
                    'label': '后台总览',
                    'description': '先看全局态势与优先任务',
                    'url': WORKBENCH_URLS['dashboard'],
                    'is_active': active_key == 'dashboard',
                },
                {
                    'label': '审核队列',
                    'description': '优先处理待审核与 AI 存疑内容',
                    'url': WORKBENCH_URLS['review_queue'],
                    'badge': metrics['pending_content_count'] or '',
                    'tone': 'danger',
                    'is_active': active_key == 'review_queue',
                },
                {
                    'label': '举报中心',
                    'description': '处理用户举报与争议内容',
                    'url': WORKBENCH_URLS['report_center'],
                    'badge': metrics['pending_reports_count'] or '',
                    'tone': 'warn',
                    'is_active': active_key == 'report_center',
                },
                {
                    'label': '内容中心',
                    'description': '按帖子或评论查看内容状态',
                    'url': WORKBENCH_URLS['content_center'],
                    'badge': metrics['ai_suspect_count'] or '',
                    'tone': 'warn',
                    'is_active': active_key == 'content_center',
                },
            ],
        },
        {
            'title': '对象中心',
            'items': [
                {
                    'label': '用户中心',
                    'description': '追踪待认证、禁言和高风险用户',
                    'url': WORKBENCH_URLS['user_center'],
                    'badge': metrics['pending_verification_count'] or '',
                    'tone': 'neutral',
                    'is_active': active_key == 'user_center',
                },
                {
                    'label': '运营配置',
                    'description': '敏感词、置顶、公告与审核留痕',
                    'url': WORKBENCH_URLS['operations_center'],
                    'badge': metrics['active_announcement_count'] or '',
                    'tone': 'neutral',
                    'is_active': active_key == 'operations_center',
                },
                {
                    'label': '推荐系统',
                    'description': '查看用户画像与推荐拆解',
                    'url': WORKBENCH_URLS['recommendation_center'],
                    'is_active': active_key == 'recommendation_center',
                },
            ],
        },
        {
            'title': '原始表单',
            'items': [
                {
                    'label': '帖子管理',
                    'url': '/admin/posts/post/',
                    'is_active': False,
                },
                {
                    'label': '评论管理',
                    'url': '/admin/comments/comment/',
                    'is_active': False,
                },
                {
                    'label': '用户管理',
                    'url': '/admin/users/user/',
                    'is_active': False,
                },
                {
                    'label': '敏感词管理',
                    'url': '/admin/moderation/sensitiveword/',
                    'is_active': False,
                },
            ],
        },
    ]


def get_admin_trends(days=7):
    now = timezone.localtime()
    start_day = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

    post_rows = {
        row['day']: row['total']
        for row in (
            Post.objects.filter(created_at__gte=start_day)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(total=Count('id'))
        )
    }
    comment_rows = {
        row['day']: row['total']
        for row in (
            Comment.objects.filter(created_at__gte=start_day)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(total=Count('id'))
        )
    }
    active_rows = {}
    for model in (Post, Comment):
        for row in (
            model.objects.filter(created_at__gte=start_day)
            .annotate(day=TruncDate('created_at'))
            .values('day', 'author_id')
        ):
            active_rows.setdefault(row['day'], set()).add(row['author_id'])

    peak = 1
    rows = []
    for index in range(days):
        day = (start_day + timedelta(days=index)).date()
        posts = post_rows.get(day, 0)
        comments = comment_rows.get(day, 0)
        users = len(active_rows.get(day, set()))
        peak = max(peak, posts, comments, users)
        rows.append({
            'label': day.strftime('%m-%d'),
            'posts': posts,
            'comments': comments,
            'users': users,
        })

    for row in rows:
        row['posts_width'] = max(8, round(row['posts'] / peak * 100)) if row['posts'] else 8
        row['comments_width'] = max(8, round(row['comments'] / peak * 100)) if row['comments'] else 8
        row['users_width'] = max(8, round(row['users'] / peak * 100)) if row['users'] else 8
    return rows


def get_review_queue(limit=10):
    report_counts = {
        item['target_id']: item['total']
        for item in (
            Report.objects.filter(status='pending', target_type='post')
            .values('target_id')
            .annotate(total=Count('id'))
        )
    }

    posts = [
        {
            'kind': '帖子',
            'id': post.id,
            'priority': 0 if report_counts.get(post.id) else (1 if post.status == 'pending' else 2),
            'status': post.get_status_display(),
            'content': content_preview(post),
            'ai_decision': post.ai_decision or 'unknown',
            'ai_reason': post.ai_reason or '等待人工审核',
            'report_count': report_counts.get(post.id, 0),
            'author': post.author.email,
            'target_link': f'/admin/workbench/moderation/post/{post.id}/',
            'author_link': f'/admin/workbench/users/{post.author_id}/',
        }
        for post in Post.objects.filter(
            Q(status='pending') | Q(status='ai_suspect'),
            is_deleted=False,
        ).select_related('author').order_by('-created_at')[:limit]
    ]
    comments = [
        {
            'kind': '评论',
            'id': comment.id,
            'priority': 1 if comment.status == 'pending' else 2,
            'status': comment.get_status_display(),
            'content': content_preview(comment),
            'ai_decision': comment.ai_decision or 'unknown',
            'ai_reason': comment.ai_reason or '等待人工审核',
            'report_count': Report.objects.filter(status='pending', target_type='comment', target_id=comment.id).count(),
            'author': comment.author.email,
            'target_link': f'/admin/workbench/moderation/comment/{comment.id}/',
            'author_link': f'/admin/workbench/users/{comment.author_id}/',
        }
        for comment in Comment.objects.filter(
            Q(status='pending') | Q(status='ai_suspect')
        ).select_related('author').order_by('-created_at')[:limit]
    ]
    rows = sorted(posts + comments, key=lambda item: (item['priority'], -item['id']))
    return rows[:limit]


def get_report_queue(limit=10):
    queryset = list(
        Report.objects.filter(status='pending')
        .select_related('user')
        .order_by('-created_at')[:limit]
    )
    post_ids = [report.target_id for report in queryset if report.target_type == 'post']
    comment_ids = [report.target_id for report in queryset if report.target_type == 'comment']
    posts = {post.id: post for post in Post.objects.filter(pk__in=post_ids).select_related('author')}
    comments = {comment.id: comment for comment in Comment.objects.filter(pk__in=comment_ids).select_related('author')}

    rows = []
    for report in queryset:
        target = posts.get(report.target_id) if report.target_type == 'post' else comments.get(report.target_id)
        author = getattr(target, 'author', None)
        rows.append({
            'id': report.id,
            'target_type': report.get_target_type_display(),
            'reason': report.reason,
            'detail': report.detail or '无补充说明',
            'reporter': report.user.email,
            'target_preview': content_preview(target) if target else '目标内容已不存在',
            'target_link': f'/admin/workbench/moderation/{report.target_type}/{report.target_id}/' if target else '',
            'report_link': f'/admin/workbench/moderation/{report.target_type}/{report.target_id}/?report_id={report.id}' if target else '',
            'author_email': author.email if author else '未知',
            'author_link': f'/admin/workbench/users/{author.id}/' if author else '',
        })
    return rows


def get_user_center(limit=8):
    pending_users = [
        {
            'id': user.id,
            'email': user.email,
            'real_name': user.real_name or '未填写姓名',
            'student_id': user.student_id or '未填写学号/工号',
        }
        for user in User.objects.filter(is_verified=False, is_staff=False).order_by('-date_joined')[:limit]
    ]
    banned_users = [
        {
            'id': user.id,
            'email': user.email,
            'ban_until': user.ban_until,
        }
        for user in User.objects.filter(is_banned=True).order_by('-ban_until', '-date_joined')[:limit]
    ]
    risky_users = sorted(
        [
            {
                'id': user.id,
                'email': user.email,
                'post_violations': user.posts.filter(status='rejected').count(),
                'comment_violations': user.comments.filter(status='rejected').count(),
            }
            for user in User.objects.filter(is_staff=False)
        ],
        key=lambda item: item['post_violations'] + item['comment_violations'],
        reverse=True,
    )
    risky_users = [item for item in risky_users if (item['post_violations'] + item['comment_violations']) > 0][:limit]
    normal_users = [
        {
            'id': user.id,
            'email': user.email,
            'post_count': user.posts.count(),
            'comment_count': user.comments.count(),
            'is_verified': user.is_verified,
        }
        for user in User.objects.filter(is_staff=False, is_banned=False)
        if user.posts.filter(status='rejected').count() + user.comments.filter(status='rejected').count() == 0
    ][:limit]
    return {
        'pending_users': pending_users,
        'banned_users': banned_users,
        'risky_users': risky_users,
        'normal_users': normal_users,
    }


def get_content_status_groups(kind):
    model = Post if kind == 'post' else Comment
    queryset = model.objects.all()
    if kind == 'post':
        queryset = queryset.filter(is_deleted=False)

    counters = {
        row['status']: row['total']
        for row in queryset.values('status').annotate(total=Count('id'))
    }
    labels = {
        'all': '全部',
        'pending': '待审核',
        'ai_suspect': 'AI 存疑',
        'normal': '正常',
        'rejected': '已下架',
    }
    order = ['all', 'pending', 'ai_suspect', 'normal', 'rejected']
    total = sum(counters.values())
    return [
        {
            'value': status,
            'label': labels[status],
            'count': total if status == 'all' else counters.get(status, 0),
        }
        for status in order
    ]


def get_content_center_snapshot(kind='post', status='', search='', limit=12):
    model = Post if kind == 'post' else Comment
    queryset = model.objects.select_related('author').order_by('-created_at')
    if kind == 'comment':
        queryset = queryset.select_related('post')
    else:
        queryset = queryset.filter(is_deleted=False)

    if status:
        queryset = queryset.filter(status=status)
    if search:
        queryset = queryset.filter(content__icontains=search)

    rows = list(queryset[:limit])
    report_counts = {
        item['target_id']: item['total']
        for item in (
            Report.objects.filter(
                status='pending',
                target_type=kind,
                target_id__in=[row.id for row in rows],
            )
            .values('target_id')
            .annotate(total=Count('id'))
        )
    }

    items = []
    for row in rows:
        if kind == 'post':
            meta = f'作者：{row.author.email} ｜ 标签：{row.tag} ｜ 风险：{row.get_risk_level_display()}'
            raw_link = f'/admin/posts/post/{row.id}/change/'
            title = f'帖子 #{row.id} · {row.tag}'
        else:
            meta = f'作者：{row.author.email} ｜ 所属帖子 #{row.post_id} ｜ 风险：{row.get_risk_level_display()}'
            raw_link = f'/admin/comments/comment/{row.id}/change/'
            title = f'评论 #{row.id} · 帖子 #{row.post_id}'

        items.append({
            'id': row.id,
            'title': title,
            'content': row.content,
            'status': row.get_status_display(),
            'status_code': row.status,
            'meta': meta,
            'ai_decision': row.ai_decision or '未执行',
            'ai_reason': row.ai_reason or '等待人工判断',
            'report_count': report_counts.get(row.id, 0),
            'target_link': f'/admin/workbench/moderation/{kind}/{row.id}/',
            'raw_link': raw_link,
        })

    primary_links = [
        {
            'label': '全部帖子',
            'value': '按最新创建时间查看帖子',
            'url': f"{WORKBENCH_URLS['content_center']}?kind=post",
        },
        {
            'label': '待审核帖子',
            'value': '优先进入待人工处理的帖子',
            'url': f"{WORKBENCH_URLS['content_center']}?kind=post&status=pending",
        },
        {
            'label': 'AI 存疑帖子',
            'value': '集中处理 AI 未能明确判断的帖子',
            'url': f"{WORKBENCH_URLS['content_center']}?kind=post&status=ai_suspect",
        },
    ] if kind == 'post' else [
        {
            'label': '全部评论',
            'value': '按最新创建时间查看评论',
            'url': f"{WORKBENCH_URLS['content_center']}?kind=comment",
        },
        {
            'label': '待审核评论',
            'value': '优先进入待人工处理的评论',
            'url': f"{WORKBENCH_URLS['content_center']}?kind=comment&status=pending",
        },
        {
            'label': 'AI 存疑评论',
            'value': '集中处理 AI 未能明确判断的评论',
            'url': f"{WORKBENCH_URLS['content_center']}?kind=comment&status=ai_suspect",
        },
    ]

    secondary_links = [
        {
            'label': '切到帖子视图' if kind == 'comment' else '切到评论视图',
            'value': '查看另一类内容的完整工作台',
            'url': f"{WORKBENCH_URLS['content_center']}?kind={'post' if kind == 'comment' else 'comment'}",
        },
        {
            'label': '进入审核队列',
            'value': '按优先级统一处理人工审核任务',
            'url': WORKBENCH_URLS['review_queue'],
        },
        {
            'label': '进入举报中心',
            'value': '从举报线索回到具体内容处理',
            'url': WORKBENCH_URLS['report_center'],
        },
    ]

    return {
        'kind': kind,
        'items': items,
        'status_groups': get_content_status_groups(kind),
        'primary_links': primary_links,
        'secondary_links': secondary_links,
    }


def get_user_detail_snapshot(user):
    posts = [
        {
            'id': post.id,
            'content': content_preview(post, 80),
            'status': post.get_status_display(),
            'risk_level': post.risk_level,
            'reason': post.moderation_reason or post.ai_reason or '正常内容',
            'link': f'/admin/posts/post/{post.id}/change/',
        }
        for post in user.posts.order_by('-created_at')[:8]
    ]
    comments = [
        {
            'id': comment.id,
            'content': content_preview(comment, 80),
            'status': comment.get_status_display(),
            'risk_level': getattr(comment, 'risk_level', 'none'),
            'reason': getattr(comment, 'moderation_reason', '') or comment.ai_reason or '正常内容',
            'link': f'/admin/comments/comment/{comment.id}/change/',
        }
        for comment in user.comments.order_by('-created_at')[:8]
    ]
    notifications = list(Notification.objects.filter(user=user).order_by('-created_at')[:8])
    return {
        'user': user,
        'stats': {
            'post_count': user.posts.count(),
            'comment_count': user.comments.count(),
            'rejected_post_count': user.posts.filter(status='rejected').count(),
            'rejected_comment_count': user.comments.filter(status='rejected').count(),
        },
        'posts': posts,
        'comments': comments,
        'notifications': notifications,
    }


def get_moderation_target(target_type, target_id):
    if target_type == 'post':
        return Post.objects.select_related('author', 'identity').filter(pk=target_id).first()
    if target_type == 'comment':
        return Comment.objects.select_related('author', 'identity', 'post').filter(pk=target_id).first()
    return None


def get_moderation_detail_snapshot(target_type, target_id):
    target = get_moderation_target(target_type, target_id)
    if not target:
        return None

    reports = list(
        Report.objects.filter(target_type=target_type, target_id=target_id)
        .select_related('user')
        .order_by('-created_at')
    )
    audits = list(
        AuditLog.objects.filter(target_type=target_type, target_id=target_id)
        .select_related('auditor')
        .order_by('-created_at')
    )
    author = target.author
    author_stats = {
        'post_count': author.posts.count(),
        'comment_count': author.comments.count(),
        'rejected_post_count': author.posts.filter(status='rejected').count(),
        'rejected_comment_count': author.comments.filter(status='rejected').count(),
    }
    return {
        'target': target,
        'target_type': target_type,
        'content_text': getattr(target, 'content', ''),
        'reports': reports,
        'pending_reports_count': len([report for report in reports if report.status == 'pending']),
        'audits': audits,
        'author': author,
        'author_stats': author_stats,
        'raw_link': f'/admin/{target_type + "s" if target_type == "post" else "comments"}/{target_type}/{target.id}/change/',
        'user_link': f'/admin/workbench/users/{author.id}/',
    }


def get_operations_center(limit=8):
    now = timezone.now()
    return {
        'hard_words_count': SensitiveWord.objects.filter(level='hard').count(),
        'soft_words_count': SensitiveWord.objects.filter(level='soft').count(),
        'pinned_posts': list(
            Post.objects.filter(is_pinned=True, is_deleted=False)
            .order_by('pinned_until', '-created_at')[:limit]
        ),
        'active_announcements': list(
            Announcement.objects.filter(is_active=True)
            .filter(Q(start_at__lte=now) | Q(start_at__isnull=True))
            .filter(Q(end_at__gte=now) | Q(end_at__isnull=True))
            .order_by('-created_at')[:limit]
        ),
        'recent_audit_logs': list(AuditLog.objects.select_related('auditor').order_by('-created_at')[:limit]),
        'recent_notifications': list(Notification.objects.select_related('user').order_by('-created_at')[:limit]),
    }
