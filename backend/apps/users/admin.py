from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from datetime import timedelta
from .models import User, AnonymousIdentity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'date_joined', 'is_banned', 'ban_until', 'post_count', 'is_active', 'is_staff']
    list_filter = ['is_banned', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('禁言', {'fields': ('is_banned', 'ban_until')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    actions = ['ban_7_days', 'ban_30_days', 'ban_forever', 'unban']

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = '发帖数'

    @admin.action(description='禁言7天')
    def ban_7_days(self, request, queryset):
        queryset.update(is_banned=True, ban_until=timezone.now() + timedelta(days=7))

    @admin.action(description='禁言30天')
    def ban_30_days(self, request, queryset):
        queryset.update(is_banned=True, ban_until=timezone.now() + timedelta(days=30))

    @admin.action(description='永久禁言')
    def ban_forever(self, request, queryset):
        queryset.update(is_banned=True, ban_until=None)

    @admin.action(description='解除禁言')
    def unban(self, request, queryset):
        queryset.update(is_banned=False, ban_until=None)


@admin.register(AnonymousIdentity)
class AnonymousIdentityAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'user', 'avatar_seed', 'created_at']
    search_fields = ['nickname', 'user__email']
    list_filter = ['created_at']
