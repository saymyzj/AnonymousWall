from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('邮箱不能为空')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('邮箱', unique=True)
    is_banned = models.BooleanField('是否禁言', default=False)
    ban_until = models.DateTimeField('禁言截止时间', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.email


class AnonymousIdentity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='identities', verbose_name='用户')
    nickname = models.CharField('匿名昵称', max_length=50)
    avatar_seed = models.CharField('头像种子', max_length=64)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'anonymous_identities'
        verbose_name = '匿名身份'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname
