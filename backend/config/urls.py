from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from common.exceptions import APIResponse
from common.admin_views import (
    content_center_view,
    dashboard_view,
    operations_center_view,
    recommendation_center_view,
    moderation_detail_view,
    report_center_view,
    review_queue_view,
    user_detail_view,
    user_center_view,
)

admin.site.site_header = '匿名宇宙 管理后台'
admin.site.site_title = '匿名宇宙 Admin'
admin.site.index_title = '内容审核与运营面板'
admin.site.index_template = 'admin/home.html'


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return APIResponse(data={'status': 'ok'}, message='匿名宇宙 API is running')


urlpatterns = [
    path('admin/workbench/dashboard/', admin.site.admin_view(dashboard_view), name='admin_dashboard'),
    path('admin/workbench/content/', admin.site.admin_view(content_center_view), name='admin_content_center'),
    path('admin/workbench/review-queue/', admin.site.admin_view(review_queue_view), name='admin_review_queue'),
    path('admin/workbench/moderation/<str:target_type>/<int:target_id>/', admin.site.admin_view(moderation_detail_view), name='admin_moderation_detail'),
    path('admin/workbench/reports/', admin.site.admin_view(report_center_view), name='admin_report_center'),
    path('admin/workbench/users/', admin.site.admin_view(user_center_view), name='admin_user_center'),
    path('admin/workbench/users/<int:user_id>/', admin.site.admin_view(user_detail_view), name='admin_user_detail'),
    path('admin/workbench/operations/', admin.site.admin_view(operations_center_view), name='admin_operations_center'),
    path('admin/workbench/recommendation/', admin.site.admin_view(recommendation_center_view), name='admin_recommendation_center'),
    path('admin/', admin.site.urls),
    path('api/health/', health_check),
    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.posts.urls')),
    path('api/', include('apps.comments.urls')),
    path('api/', include('apps.interactions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
