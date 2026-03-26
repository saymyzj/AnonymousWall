from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview', 'post', 'status', 'like_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['content']
    actions = ['mark_rejected', 'mark_normal']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容摘要'

    @admin.action(description='下架选中评论')
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')

    @admin.action(description='恢复选中评论')
    def mark_normal(self, request, queryset):
        queryset.update(status='normal')
