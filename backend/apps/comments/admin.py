from django.contrib import admin
from django.utils import timezone

from apps.interactions.models import Notification
from apps.moderation.models import AuditLog

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview', 'post', 'author_email', 'status', 'risk_level_display', 'review_deadline', 'ai_decision_display', 'like_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['content', 'author__email', 'identity__nickname', 'ai_reason']
    list_select_related = ['post', 'author', 'identity']
    readonly_fields = ['ai_decision', 'ai_reason', 'moderation_reason', 'created_at', 'reviewed_at']
    actions = ['mark_pending', 'mark_rejected', 'mark_normal']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容摘要'

    def author_email(self, obj):
        return obj.author.email
    author_email.short_description = '作者邮箱'

    def ai_decision_display(self, obj):
        mapping = {
            'accept': '通过',
            'confuse': '待复核',
            'reject': '高风险',
            'unknown': '待复核',
            'not_run': '未执行',
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
                target_type='comment',
                target_id=comment.id,
                action=action,
                reason=reason,
            )
            for comment in queryset
        ]
        if logs:
            AuditLog.objects.bulk_create(logs)

    @admin.action(description='标记为待审核')
    def mark_pending(self, request, queryset):
        queryset.update(status='pending', reviewed_at=None)

    @admin.action(description='下架选中评论')
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected', moderation_source='manual', reviewed_at=timezone.now(), review_deadline=None)
        self._log_bulk_action(request, queryset, 'reject', '管理员在后台下架了评论')
        Notification.objects.bulk_create([
            Notification(
                user=comment.author,
                type='system',
                title='你的评论已被管理员下架',
                content='你发布的一条评论因审核原因被下架。',
                link=f'/post/{comment.post_id}#comments',
            )
            for comment in queryset
        ])

    @admin.action(description='恢复选中评论')
    def mark_normal(self, request, queryset):
        queryset.update(status='normal', moderation_source='manual', reviewed_at=timezone.now(), review_deadline=None)
        self._log_bulk_action(request, queryset, 'approve', '管理员在后台恢复了评论')
