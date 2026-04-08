from apps.users.models import User

from .reset_demo_data import Command as ResetDemoDataCommand


class Command(ResetDemoDataCommand):
    help = '清空数据库并生成轻量级演示数据，适合 Web 函数冷启动演示环境'

    USER_COUNT = 18
    POST_COUNT = 48

    def _create_users(self):
        users = []
        preferences = {}
        for index in range(self.USER_COUNT):
            # Keep most users verified in the light dataset so post generation
            # still has enough candidates under small sample sizes.
            verified = index >= 3
            banned = verified and index % 11 == 0 and index < 12
            user = User.objects.create_user(
                email=f'light{index + 1:03d}@example.com',
                password='Demo123456',
                real_name=self._build_name(index),
                student_id=f'L2026{index + 1:04d}',
                is_verified=verified,
                is_banned=banned,
                ban_until=self.now + self._ban_delta() if banned else None,
            )
            preferences[user.id] = self.rng.sample(self.TAGS, 2)
            users.append(user)
        return users, preferences

    def _ban_delta(self):
        from datetime import timedelta

        return timedelta(days=self.rng.choice([3, 7, 15]))
