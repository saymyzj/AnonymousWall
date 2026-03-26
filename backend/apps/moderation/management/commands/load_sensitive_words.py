from django.core.management.base import BaseCommand
from apps.moderation.models import SensitiveWord


DEFAULT_HARD_WORDS = [
    '杀人', '自杀指南', '贩毒', '枪支', '炸弹',
]

DEFAULT_SOFT_WORDS = [
    '傻逼', '草泥马', '废物', '垃圾人', '去死',
    '白痴', '智障', '脑残', '贱人', '滚蛋',
]


class Command(BaseCommand):
    help = '加载默认敏感词库'

    def handle(self, *args, **options):
        count = 0
        for word in DEFAULT_HARD_WORDS:
            _, created = SensitiveWord.objects.get_or_create(
                word=word, defaults={'level': 'hard'}
            )
            if created:
                count += 1

        for word in DEFAULT_SOFT_WORDS:
            _, created = SensitiveWord.objects.get_or_create(
                word=word, defaults={'level': 'soft'}
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'成功加载 {count} 个敏感词'))
