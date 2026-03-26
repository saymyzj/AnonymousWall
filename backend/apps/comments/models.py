from django.db import models
from apps.users.models import User, AnonymousIdentity
from apps.posts.models import Post


class Comment(models.Model):
    STATUS_CHOICES = [
        ('normal', '正常'), ('ai_suspect', 'AI存疑'),
        ('pending', '待审核'), ('rejected', '已下架'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='帖子')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='作者')
    identity = models.ForeignKey(AnonymousIdentity, on_delete=models.SET_NULL, null=True, verbose_name='匿名身份')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    content = models.TextField('内容', max_length=200)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='normal')
    like_count = models.IntegerField('点赞数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'comments'
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f'{self.content[:30]}'
