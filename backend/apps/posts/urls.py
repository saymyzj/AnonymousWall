from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.post_list, name='post_list'),
    path('home/meta/', views.home_meta, name='home_meta'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.update_post, name='update_post'),
    path('posts/<int:pk>/vote/', views.vote_poll, name='vote_poll'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
]
