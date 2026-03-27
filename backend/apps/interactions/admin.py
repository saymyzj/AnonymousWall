from django.contrib import admin
from django.utils import timezone
from datetime import timedelta

from apps.comments.models import Comment
from apps.moderation.models import AuditLog
from apps.posts.models import Post

from .models import Conversation, Favorite, Like, Notification, PrivateMessage, Report


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_type', 'target_id', 'created_at']
    list_filter = ['target_type', 'created_at']
    search_fields = ['user__email']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_type', 'target_id', 'created_at']
    list_filter = ['target_type', 'created_at']
    search_fields = ['user__email']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'target_type', 'target_id', 'target_preview', 'reason', 'status', 'created_at']
    list_filter = ['target_type', 'reason', 'status', 'created_at']
    search_fields = ['user__email', 'detail']
    readonly_fields = ['target_preview', 'detail', 'created_at']
    actions = ['mark_resolved', 'resolve_and_reject_content', 'resolve_reject_and_ban_7_days', 'mark_ignored']

    def _get_target(self, report):
        if report.target_type == 'post':
            return Post.objects.filter(pk=report.target_id).first()
        return Comment.objects.filter(pk=report.target_id).first()

    def target_preview(self, obj):
        target = self._get_target(obj)
        if not target:
            return '目标不存在'
        content = getattr(target, 'content', '')
        return content[:40] + '...' if len(content) > 40 else content
    target_preview.short_description = '举报内容'

    @admin.action(description='标记为已处理')
    def mark_resolved(self, request, queryset):
        for report in queryset:
            report.status = 'resolved'
            report.save(update_fields=['status'])
            Notification.objects.create(
                user=report.user,
                type='report',
                title='你举报的内容已处理',
                content='管理员已处理你提交的举报，感谢你的反馈。',
                link='/messages?tab=notifications',
                is_read=False,
            )

    @admin.action(description='下架被举报内容并结案')
    def resolve_and_reject_content(self, request, queryset):
        for report in queryset:
            target = self._get_target(report)
            if target and hasattr(target, 'status'):
                target.status = 'rejected'
                if hasattr(target, 'moderation_source'):
                    target.moderation_source = 'manual'
                if hasattr(target, 'moderation_reason'):
                    target.moderation_reason = f'管理员根据举报下架内容，举报原因：{report.reason}'
                if hasattr(target, 'reviewed_at'):
                    target.reviewed_at = timezone.now()
                if hasattr(target, 'review_deadline'):
                    target.review_deadline = None
                update_fields = ['status']
                if hasattr(target, 'moderation_source'):
                    update_fields.append('moderation_source')
                if hasattr(target, 'moderation_reason'):
                    update_fields.append('moderation_reason')
                if hasattr(target, 'reviewed_at'):
                    update_fields.append('reviewed_at')
                if hasattr(target, 'review_deadline'):
                    update_fields.append('review_deadline')
                target.save(update_fields=update_fields)
                AuditLog.objects.create(
                    auditor=request.user,
                    target_type=report.target_type,
                    target_id=report.target_id,
                    action='reject',
                    reason=f'管理员根据举报下架内容，举报原因：{report.reason}',
                )
                Notification.objects.create(
                    user=target.author,
                    type='system',
                    title='你的内容因举报已被下架',
                    content=f'管理员已处理举报，原因：{report.reason}',
                    link=f'/post/{target.post_id if report.target_type == "comment" else target.id}',
                    is_read=False,
                )

            report.status = 'resolved'
            report.save(update_fields=['status'])
            Notification.objects.create(
                user=report.user,
                type='report',
                title='你举报的内容已处理',
                content='管理员已根据举报结果处理相关内容。',
                link='/messages?tab=notifications',
                is_read=False,
            )

    @admin.action(description='下架内容并禁言作者 7 天')
    def resolve_reject_and_ban_7_days(self, request, queryset):
        for report in queryset:
            target = self._get_target(report)
            if target and hasattr(target, 'status'):
                target.status = 'rejected'
                if hasattr(target, 'moderation_source'):
                    target.moderation_source = 'manual'
                if hasattr(target, 'moderation_reason'):
                    target.moderation_reason = f'管理员根据举报下架内容并禁言作者 7 天，举报原因：{report.reason}'
                if hasattr(target, 'reviewed_at'):
                    target.reviewed_at = timezone.now()
                if hasattr(target, 'review_deadline'):
                    target.review_deadline = None
                update_fields = ['status']
                if hasattr(target, 'moderation_source'):
                    update_fields.append('moderation_source')
                if hasattr(target, 'moderation_reason'):
                    update_fields.append('moderation_reason')
                if hasattr(target, 'reviewed_at'):
                    update_fields.append('reviewed_at')
                if hasattr(target, 'review_deadline'):
                    update_fields.append('review_deadline')
                target.save(update_fields=update_fields)
                target.author.is_banned = True
                target.author.ban_until = timezone.now() + timedelta(days=7)
                target.author.save(update_fields=['is_banned', 'ban_until'])
                AuditLog.objects.create(
                    auditor=request.user,
                    target_type=report.target_type,
                    target_id=report.target_id,
                    action='ban',
                    reason=f'管理员根据举报下架内容并禁言作者 7 天，举报原因：{report.reason}',
                )
                Notification.objects.create(
                    user=target.author,
                    type='system',
                    title='你的内容被下架且账号已禁言 7 天',
                    content=f'管理员已处理举报，原因：{report.reason}',
                    link=f'/post/{target.post_id if report.target_type == "comment" else target.id}',
                    is_read=False,
                )

            report.status = 'resolved'
            report.save(update_fields=['status'])
            Notification.objects.create(
                user=report.user,
                type='report',
                title='你举报的内容已处理',
                content='管理员已处理举报并对相关账号采取处罚。',
                link='/messages?tab=notifications',
                is_read=False,
            )

    @admin.action(description='忽略举报')
    def mark_ignored(self, request, queryset):
        queryset.update(status='ignored')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'owner', 'participant', 'message_count', 'is_blocked', 'updated_at']
    list_filter = ['is_blocked', 'updated_at']
    search_fields = ['owner__email', 'participant__email', 'post__content']

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = '消息数'


@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'content', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__email']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'title', 'is_read', 'is_ignored', 'created_at']
    list_filter = ['type', 'is_read', 'is_ignored', 'created_at']
    search_fields = ['user__email', 'title', 'content']
