from django.urls import path
from . import views

urlpatterns = [
    path('posts/<int:pk>/like/', views.toggle_post_like, name='toggle_post_like'),
    path('posts/<int:pk>/favorite/', views.toggle_post_favorite, name='toggle_post_favorite'),
    path('comments/<int:pk>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('reports/create/', views.create_report, name='create_report'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/read-all/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/<int:pk>/ignore/', views.ignore_notification, name='ignore_notification'),
    path('messages/conversations/', views.conversation_list, name='conversation_list'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/conversations/<int:conversation_id>/reply/', views.reply_message, name='reply_message'),
    path('messages/conversations/<int:conversation_id>/block/', views.block_conversation, name='block_conversation'),
]
