from django.contrib import admin
from .models import SensitiveWord, AuditLog
from .services import DFAFilter


@admin.register(SensitiveWord)
class SensitiveWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'level', 'created_at']
    list_filter = ['level']
    search_fields = ['word']
    list_editable = ['level']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        DFAFilter.rebuild()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        DFAFilter.rebuild()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        DFAFilter.rebuild()


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['target_type', 'target_id', 'action', 'auditor', 'reason', 'created_at']
    list_filter = ['action', 'target_type', 'created_at']
    readonly_fields = ['auditor', 'target_type', 'target_id', 'action', 'reason', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
