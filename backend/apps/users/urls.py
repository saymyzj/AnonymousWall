from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.me, name='me'),
    path('preferences/', views.update_preferences, name='update_preferences'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('identities/refresh/', views.refresh_identity, name='refresh_identity'),
]
