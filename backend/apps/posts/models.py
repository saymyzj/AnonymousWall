from django.db import models
from apps.users.models import User, AnonymousIdentity


class Post(models.Model):
    TAG_CHOICES = [
        ('表白', '表白'), ('吐槽', '吐槽'), ('求助', '求助'),
        ('树洞', '树洞'), ('失物招领', '失物招领'), ('搭子', '搭子'),
    ]
    BG_COLORS = [
        (1, '樱花粉'), (2, '蜜桃橘'), (3, '薄荷青'), (4, '天空蓝'),
        (5, '薰衣紫'), (6, '柠檬黄'), (7, '云雾白'), (8, '奶茶棕'),
    ]
    STATUS_CHOICES = [
        ('normal', '正常'), ('ai_suspect', 'AI存疑'),
        ('pending', '待审核'), ('rejected', '已下架'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='作者')
    identity = models.ForeignKey(AnonymousIdentity, on_delete=models.SET_NULL, null=True, verbose_name='匿名身份')
    content = models.TextField('内容', max_length=500)
    tag = models.CharField('标签', max_length=20, choices=TAG_CHOICES)
    bg_color = models.IntegerField('背景色', choices=BG_COLORS, default=7)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='normal')
    is_deleted = models.BooleanField('已删除', default=False)
    like_count = models.IntegerField('点赞数', default=0)
    comment_count = models.IntegerField('评论数', default=0)
    favorite_count = models.IntegerField('收藏数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'posts'
        verbose_name = '帖子'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.identity.nickname if self.identity else "未知"}: {self.content[:30]}'
