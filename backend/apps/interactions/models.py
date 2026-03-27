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


class Favorite(models.Model):
    TARGET_CHOICES = [('post', '帖子')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    target_type = models.CharField('目标类型', max_length=10, choices=TARGET_CHOICES, default='post')
    target_id = models.IntegerField('目标ID')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'target_type', 'target_id']

    def __str__(self):
        return f'{self.user.email} favorite -> {self.target_type}:{self.target_id}'


class Report(models.Model):
    TARGET_CHOICES = [('post', '帖子'), ('comment', '评论')]
    REASON_CHOICES = [
        ('广告引流', '广告引流'),
        ('人身攻击', '人身攻击'),
        ('色情低俗', '色情低俗'),
        ('隐私泄露', '隐私泄露'),
        ('其他', '其他'),
    ]
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('resolved', '已处理'),
        ('ignored', '已忽略'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name='举报人')
    target_type = models.CharField('目标类型', max_length=10, choices=TARGET_CHOICES)
    target_id = models.IntegerField('目标ID')
    reason = models.CharField('举报原因', max_length=20, choices=REASON_CHOICES)
    detail = models.CharField('补充说明', max_length=100, blank=True, default='')
    status = models.CharField('处理状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'reports'
        verbose_name = '举报'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'target_type', 'target_id']

    def __str__(self):
        return f'{self.user.email} report -> {self.target_type}:{self.target_id}'


class Conversation(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='conversations', verbose_name='关联帖子')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_conversations', verbose_name='楼主')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participating_conversations', verbose_name='发起方')
    is_blocked = models.BooleanField('是否已拉黑', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'conversations'
        verbose_name = '私信会话'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']
        unique_together = ['post', 'owner', 'participant']

    def __str__(self):
        return f'{self.post_id}:{self.participant_id}->{self.owner_id}'


class PrivateMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name='会话')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='private_messages', verbose_name='发送者')
    content = models.CharField('消息内容', max_length=300)
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'private_messages'
        verbose_name = '私信消息'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f'{self.conversation_id}:{self.sender_id}'


class Notification(models.Model):
    TYPE_CHOICES = [
        ('comment', '评论'),
        ('like', '点赞'),
        ('favorite', '收藏'),
        ('report', '举报'),
        ('system', '系统'),
        ('message', '私信'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收用户')
    type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES)
    title = models.CharField('标题', max_length=120)
    content = models.CharField('内容', max_length=300)
    link = models.CharField('跳转链接', max_length=255, blank=True, default='')
    is_read = models.BooleanField('是否已读', default=False)
    is_ignored = models.BooleanField('是否已忽略', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = '站内通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email}:{self.type}'
