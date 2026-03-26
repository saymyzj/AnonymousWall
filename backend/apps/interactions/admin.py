from django.contrib import admin
from .models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_type', 'target_id', 'created_at']
    list_filter = ['target_type', 'created_at']
