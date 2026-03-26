from django.urls import path
from . import views

urlpatterns = [
    path('posts/<int:post_id>/comments/', views.comment_list, name='comment_list'),
    path('posts/<int:post_id>/comments/create/', views.create_comment, name='create_comment'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]
