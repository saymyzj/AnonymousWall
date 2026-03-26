from django.db import models
from apps.users.models import User


class Like(models.Model):
    TARGET_CHOICES = [('post', '帖子'), ('comment', '评论')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name='用户')
    target_type = models.CharField('目标类型', max_length=10, choices=TARGET_CHOICES)
    target_id = models.IntegerField('目标ID')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'likes'
        verbose_name = '点赞'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'target_type', 'target_id']

    def __str__(self):
        return f'{self.user.email} -> {self.target_type}:{self.target_id}'
