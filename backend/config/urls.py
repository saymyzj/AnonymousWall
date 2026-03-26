from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from common.exceptions import APIResponse


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return APIResponse(data={'status': 'ok'}, message='AnonymousWall API is running')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check),
    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.posts.urls')),
    path('api/', include('apps.comments.urls')),
    path('api/', include('apps.interactions.urls')),
]
