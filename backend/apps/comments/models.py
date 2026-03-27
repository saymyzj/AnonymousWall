from django.db import models
from apps.users.models import User, AnonymousIdentity
from apps.posts.models import Post


class Comment(models.Model):
    STATUS_CHOICES = [
        ('normal', '正常'), ('ai_suspect', 'AI存疑'),
        ('pending', '待审核'), ('rejected', '已下架'),
    ]
    MODERATION_SOURCE_CHOICES = [
        ('none', '未触发'),
        ('hard_word', '硬拦截'),
        ('soft_word', '软标记'),
        ('ai', 'AI审核'),
        ('manual', '人工审核'),
    ]
    RISK_LEVEL_CHOICES = [
        ('none', '无'),
        ('low', '低风险'),
        ('medium', '中风险'),
        ('high', '高风险'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='帖子')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='作者')
    identity = models.ForeignKey(AnonymousIdentity, on_delete=models.SET_NULL, null=True, verbose_name='匿名身份')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    content = models.TextField('内容', max_length=200)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='normal')
    ai_decision = models.CharField('AI审核结论', max_length=20, blank=True, default='')
    ai_reason = models.TextField('AI审核原因', blank=True, default='')
    moderation_source = models.CharField('审核来源', max_length=20, choices=MODERATION_SOURCE_CHOICES, default='none')
    moderation_reason = models.TextField('审核/违规原因', blank=True, default='')
    risk_level = models.CharField('风险等级', max_length=10, choices=RISK_LEVEL_CHOICES, default='none')
    review_deadline = models.DateTimeField('审核截止时间', null=True, blank=True)
    reviewed_at = models.DateTimeField('人工审核时间', null=True, blank=True)
    like_count = models.IntegerField('点赞数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'comments'
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f'{self.content[:30]}'
