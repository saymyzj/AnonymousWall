from datetime import timedelta

from django.db import models
from django.utils import timezone
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

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='作者')
    identity = models.ForeignKey(AnonymousIdentity, on_delete=models.SET_NULL, null=True, verbose_name='匿名身份')
    content = models.TextField('内容', max_length=500)
    tag = models.CharField('标签', max_length=20, choices=TAG_CHOICES)
    bg_color = models.IntegerField('背景色', choices=BG_COLORS, default=7)
    allow_messages = models.BooleanField('允许私信', default=True)
    destroy_after_hours = models.PositiveIntegerField('自毁时长(小时)', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='normal')
    is_deleted = models.BooleanField('已删除', default=False)
    is_pinned = models.BooleanField('是否置顶', default=False)
    pinned_until = models.DateTimeField('置顶截止时间', null=True, blank=True)
    ai_decision = models.CharField('AI审核结论', max_length=20, blank=True, default='')
    ai_reason = models.TextField('AI审核原因', blank=True, default='')
    moderation_source = models.CharField('审核来源', max_length=20, choices=MODERATION_SOURCE_CHOICES, default='none')
    moderation_reason = models.TextField('审核/违规原因', blank=True, default='')
    risk_level = models.CharField('风险等级', max_length=10, choices=RISK_LEVEL_CHOICES, default='none')
    review_deadline = models.DateTimeField('审核截止时间', null=True, blank=True)
    reviewed_at = models.DateTimeField('人工审核时间', null=True, blank=True)
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

    @property
    def expires_at(self):
        if not self.destroy_after_hours:
            return None
        return self.created_at + timedelta(hours=self.destroy_after_hours)

    @property
    def is_expired(self):
        expires_at = self.expires_at
        return bool(expires_at and expires_at <= timezone.now())


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name='帖子')
    image = models.ImageField('图片', upload_to='posts/')
    thumbnail = models.ImageField('缩略图', upload_to='posts/thumbnails/', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'post_images'
        verbose_name = '帖子图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.post_id}:{self.id}'


class Poll(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='poll', verbose_name='帖子')
    question = models.CharField('问题', max_length=120, blank=True, default='')
    expire_days = models.PositiveIntegerField('截止天数', default=3)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'polls'
        verbose_name = '投票'
        verbose_name_plural = verbose_name


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options', verbose_name='投票')
    text = models.CharField('选项内容', max_length=30)
    vote_count = models.PositiveIntegerField('票数', default=0)

    class Meta:
        db_table = 'poll_options'
        verbose_name = '投票选项'
        verbose_name_plural = verbose_name


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes', verbose_name='投票')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes', verbose_name='选项')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes', verbose_name='用户')
    created_at = models.DateTimeField('投票时间', auto_now_add=True)

    class Meta:
        db_table = 'poll_votes'
        verbose_name = '投票记录'
        verbose_name_plural = verbose_name
        unique_together = ['poll', 'user']


class Announcement(models.Model):
    title = models.CharField('标题', max_length=120)
    content = models.TextField('正文', max_length=500)
    is_active = models.BooleanField('是否启用', default=True)
    start_at = models.DateTimeField('展示开始时间', null=True, blank=True)
    end_at = models.DateTimeField('展示结束时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'announcements'
        verbose_name = '系统公告'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title
