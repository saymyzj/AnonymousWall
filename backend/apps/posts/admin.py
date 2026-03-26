from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview', 'tag', 'status', 'author_email', 'like_count', 'comment_count', 'created_at']
    list_filter = ['status', 'tag', 'created_at']
    search_fields = ['content']
    list_editable = ['status']
    actions = ['mark_rejected', 'mark_normal']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容摘要'

    def author_email(self, obj):
        return obj.author.email
    author_email.short_description = '作者邮箱'

    @admin.action(description='下架选中帖子')
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')

    @admin.action(description='恢复选中帖子')
    def mark_normal(self, request, queryset):
        queryset.update(status='normal')
