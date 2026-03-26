from django.db import models
from apps.users.models import User


class SensitiveWord(models.Model):
    LEVEL_CHOICES = [('hard', '硬拦截'), ('soft', '软标记')]

    word = models.CharField('敏感词', max_length=100, unique=True)
    level = models.CharField('级别', max_length=10, choices=LEVEL_CHOICES, default='soft')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sensitive_words'
        verbose_name = '敏感词'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.word} ({self.get_level_display()})'


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('approve', '通过'), ('reject', '下架'), ('ban', '禁言'),
    ]

    auditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='审核人')
    target_type = models.CharField('目标类型', max_length=20)
    target_id = models.IntegerField('目标ID')
    action = models.CharField('操作', max_length=20, choices=ACTION_CHOICES)
    reason = models.TextField('原因', blank=True, default='')
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审核记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_action_display()} {self.target_type}:{self.target_id}'
