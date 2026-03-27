from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

from apps.interactions.models import Notification, Report
from apps.moderation.models import AuditLog

from .models import Announcement, Poll, PollOption, PollVote, Post, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    fields = ['image', 'thumbnail', 'created_at']
    readonly_fields = ['created_at']


class PollInline(admin.StackedInline):
    model = Poll
    extra = 0
    max_num = 1
    fields = ['question', 'expire_days', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInline, PollInline]
    list_display = [
        'id', 'content_preview', 'tag', 'status', 'is_pinned',
        'allow_messages', 'author_email', 'report_count', 'risk_level_display', 'review_deadline',
        'ai_decision_display', 'like_count', 'comment_count', 'favorite_count', 'created_at',
    ]
    list_filter = ['status', 'tag', 'allow_messages', 'is_pinned', 'created_at']
    search_fields = ['content', 'author__email', 'identity__nickname', 'ai_reason']
    list_select_related = ['author', 'identity']
    readonly_fields = ['ai_decision', 'ai_reason', 'moderation_reason', 'expires_at_display', 'report_count', 'created_at', 'updated_at', 'reviewed_at']
    actions = ['mark_pending', 'mark_ai_suspect', 'mark_rejected', 'mark_normal', 'pin_7_days', 'unpin_posts', 'soft_delete_posts']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容摘要'

    def author_email(self, obj):
        return obj.author.email
    author_email.short_description = '作者邮箱'

    def report_count(self, obj):
        return Report.objects.filter(target_type='post', target_id=obj.id).count()
    report_count.short_description = '举报数'

    def expires_at_display(self, obj):
        return obj.expires_at or '不过期'
    expires_at_display.short_description = '自毁时间'

    def ai_decision_display(self, obj):
        mapping = {
            'safe': '安全',
            'review': '待复核',
            'reject': '高风险',
            'unknown': '待复核',
            'unknow': '待复核',
            '': '未审核',
        }
        return mapping.get(obj.ai_decision, obj.ai_decision)
    ai_decision_display.short_description = 'AI审核结果'

    def risk_level_display(self, obj):
        return {
            'high': '高风险',
            'medium': '中风险',
            'low': '低风险',
            'none': '无',
        }.get(obj.risk_level, obj.risk_level)
    risk_level_display.short_description = '风险等级'

    def _log_bulk_action(self, request, queryset, action, reason):
        logs = [
            AuditLog(
                auditor=request.user,
                target_type='post',
                target_id=post.id,
                action=action,
                reason=reason,
            )
            for post in queryset
        ]
        if logs:
            AuditLog.objects.bulk_create(logs)

    def _notify_authors(self, queryset, title, content_builder):
        notifications = [
            Notification(
                user=post.author,
                type='system',
                title=title,
                content=content_builder(post),
                link=f'/post/{post.id}',
            )
            for post in queryset
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)

    @admin.action(description='标记为待审核')
    def mark_pending(self, request, queryset):
        queryset.update(status='pending', reviewed_at=None)

    @admin.action(description='标记为 AI 存疑')
    def mark_ai_suspect(self, request, queryset):
        queryset.update(status='ai_suspect', reviewed_at=None)

    @admin.action(description='下架选中帖子')
    def mark_rejected(self, request, queryset):
        queryset.update(
            status='rejected',
            moderation_source='manual',
            reviewed_at=timezone.now(),
            review_deadline=None,
        )
        self._log_bulk_action(request, queryset, 'reject', '管理员在后台下架了帖子')
        self._notify_authors(queryset, '你的帖子已被管理员下架', lambda post: f'帖子「{post.tag}」因审核原因已被下架。')

    @admin.action(description='恢复选中帖子')
    def mark_normal(self, request, queryset):
        queryset.update(
            status='normal',
            moderation_source='manual',
            reviewed_at=timezone.now(),
            review_deadline=None,
        )
        self._log_bulk_action(request, queryset, 'approve', '管理员在后台恢复了帖子')

    @admin.action(description='置顶 7 天')
    def pin_7_days(self, request, queryset):
        queryset.update(is_pinned=True, pinned_until=timezone.now() + timedelta(days=7))

    @admin.action(description='取消置顶')
    def unpin_posts(self, request, queryset):
        queryset.update(is_pinned=False, pinned_until=None)

    @admin.action(description='软删除选中帖子')
    def soft_delete_posts(self, request, queryset):
        queryset.update(is_deleted=True)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'start_at', 'end_at', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'content']


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 0
    fields = ['text', 'vote_count']
    readonly_fields = ['vote_count']


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'question', 'expire_days', 'total_votes', 'created_at']
    search_fields = ['post__content', 'question']
    list_filter = ['expire_days', 'created_at']
    readonly_fields = ['created_at', 'total_votes']
    inlines = [PollOptionInline]

    def total_votes(self, obj):
        return sum(option.vote_count for option in obj.options.all())
    total_votes.short_description = '总票数'


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'created_at']
    search_fields = ['post__content']
    list_filter = ['created_at']


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'poll', 'text', 'vote_count']
    search_fields = ['text', 'poll__question', 'poll__post__content']


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'poll', 'option', 'user', 'created_at']
    search_fields = ['user__email', 'option__text', 'poll__question']
    list_filter = ['created_at']
