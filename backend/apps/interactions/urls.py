from django.urls import path
from . import views

urlpatterns = [
    path('posts/<int:pk>/like/', views.toggle_post_like, name='toggle_post_like'),
    path('comments/<int:pk>/like/', views.toggle_comment_like, name='toggle_comment_like'),
]
