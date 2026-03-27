import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.comments.models import Comment
from apps.interactions.models import Conversation, Favorite, Like, Notification, PrivateMessage, Report
from apps.moderation.models import AuditLog, SensitiveWord
from apps.posts.models import Announcement, Post
from apps.users.models import AnonymousIdentity, User
from apps.users.utils import generate_avatar_seed, generate_nickname


class Command(BaseCommand):
    help = '删除测试用户/测试数据，并重新生成一套更真实的演示数据'

    def handle(self, *args, **options):
        random.seed(20260327)
        self.stdout.write('开始清理旧测试数据...')

        Notification.objects.exclude(user__is_staff=True).delete()
        Report.objects.all().delete()
        Like.objects.all().delete()
        Favorite.objects.all().delete()
        PrivateMessage.objects.all().delete()
        Conversation.objects.all().delete()
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Announcement.objects.all().delete()
        AuditLog.objects.all().delete()
        AnonymousIdentity.objects.filter(user__is_staff=False).delete()
        User.objects.filter(is_staff=False).delete()

        SensitiveWord.objects.all().delete()
        SensitiveWord.objects.bulk_create([
            SensitiveWord(word='硬测词', level='hard'),
            SensitiveWord(word='软测词', level='soft'),
            SensitiveWord(word='广告引流', level='soft'),
            SensitiveWord(word='裸聊', level='hard'),
        ])

        self.stdout.write('开始生成演示用户...')
        sample_users = [
            ('linyue', '林月', '20260001', True, False),
            ('zhouchen', '周辰', '20260002', True, False),
            ('wangnan', '王楠', '20260003', True, False),
            ('liuyu', '刘雨', '20260004', True, False),
            ('hejia', '何嘉', '20260005', True, False),
            ('sunting', '孙婷', '20260006', True, False),
            ('gaohan', '高涵', '20260007', False, False),
            ('qimeng', '齐萌', '20260008', True, True),
        ]
        users = []
        for username, real_name, student_id, verified, banned in sample_users:
            user = User.objects.create_user(
                email=f'{username}@example.com',
                password='Demo123456',
                student_id=student_id,
                real_name=real_name,
                is_verified=verified,
                is_banned=banned,
                ban_until=timezone.now() + timedelta(days=5) if banned else None,
            )
            for _ in range(2):
                AnonymousIdentity.objects.create(
                    user=user,
                    nickname=generate_nickname(),
                    avatar_seed=generate_avatar_seed(),
                )
            users.append(user)

        self.stdout.write('开始生成帖子与评论...')
        tag_pool = ['树洞', '求助', '表白', '吐槽', '搭子', '失物招领']
        content_pool = [
            '今天图书馆三楼靠窗的位置真的很舒服，适合发呆和写作业。',
            '有没有人想一起晨跑，最近想坚持一个月打卡。',
            '食堂新出的番茄牛腩面比预期好吃，值得试试。',
            '求助，数据结构作业最后一题一直卡住，有没有人愿意一起看看。',
            '昨晚操场的晚风很舒服，突然觉得校园生活也没那么糟。',
            '有没有人周末想去看展，想找个搭子一起走走。',
            '今天捡到一把黑色折叠伞，失主可以联系我确认细节。',
            '最近宿舍作息完全对不上，真的有点崩溃。',
            '表白一下那个总是帮别人扶门的人，细节真的很加分。',
            '想找一起学英语口语的小伙伴，互相监督会更容易坚持。',
        ]

        posts = []
        now = timezone.now()
        for index in range(18):
            author = random.choice(users[:6])
            identity = author.identities.order_by('-created_at').first()
            post = Post.objects.create(
                author=author,
                identity=identity,
                content=random.choice(content_pool),
                tag=random.choice(tag_pool),
                bg_color=random.randint(1, 8),
                allow_messages=random.choice([True, True, False]),
                status='normal',
                moderation_source='ai',
                moderation_reason='正常内容',
                ai_decision='accept',
                ai_reason='内容正常',
                risk_level='none',
                created_at=now - timedelta(hours=random.randint(1, 120)),
                updated_at=now - timedelta(hours=random.randint(1, 48)),
            )
            posts.append(post)

        posts[2].status = 'ai_suspect'
        posts[2].risk_level = 'medium'
        posts[2].moderation_source = 'soft_word'
        posts[2].moderation_reason = '命中软标记敏感词：广告引流'
        posts[2].review_deadline = now + timedelta(days=7)
        posts[2].reviewed_at = None
        posts[2].save()

        posts[5].status = 'rejected'
        posts[5].risk_level = 'high'
        posts[5].moderation_source = 'ai'
        posts[5].moderation_reason = 'AI 审核判定为高风险内容'
        posts[5].ai_decision = 'reject'
        posts[5].ai_reason = '存在明显违规表达'
        posts[5].reviewed_at = now
        posts[5].save()

        for post in posts[:3]:
            post.is_pinned = True
            post.pinned_until = now + timedelta(days=3)
            post.save(update_fields=['is_pinned', 'pinned_until'])

        for post in posts:
            comment_total = random.randint(0, 4)
            for _ in range(comment_total):
                author = random.choice(users[:6])
                identity = author.identities.order_by('-created_at').first()
                Comment.objects.create(
                    post=post,
                    author=author,
                    identity=identity,
                    content=random.choice(content_pool)[:80],
                    status='normal',
                    moderation_source='ai',
                    moderation_reason='正常内容',
                    ai_decision='accept',
                    ai_reason='内容正常',
                    risk_level='none',
                )
            post.comment_count = post.comments.filter(status__in=['normal', 'ai_suspect']).count()
            post.like_count = random.randint(0, 14)
            post.favorite_count = random.randint(0, 6)
            post.save(update_fields=['comment_count', 'like_count', 'favorite_count'])

        sample_reports = [
            (users[1], posts[2], '广告引流', '这个内容看起来像在引流'),
            (users[2], posts[5], '人身攻击', '语气很不友好'),
            (users[3], posts[1].comments.first(), '其他', '评论内容不太合适'),
        ]
        for reporter, target, reason, detail in sample_reports:
            if target is None:
                continue
            Report.objects.create(
                user=reporter,
                target_type='comment' if isinstance(target, Comment) else 'post',
                target_id=target.id,
                reason=reason,
                detail=detail,
                status='pending',
            )

        for user in users[:4]:
            Notification.objects.create(
                user=user,
                type='system',
                title='欢迎来到 AnonymousWall',
                content='这是一组新的演示数据，你现在看到的内容已重新生成。',
                link='/',
            )

        Announcement.objects.create(
            title='演示环境已刷新',
            content='后台和前台内容均已根据最新规则重新生成。',
            is_active=True,
            start_at=now - timedelta(hours=1),
            end_at=now + timedelta(days=7),
        )

        if len(users) >= 2:
            conversation = Conversation.objects.create(post=posts[0], owner=users[0], participant=users[1])
            PrivateMessage.objects.create(conversation=conversation, sender=users[1], content='你好，想问一下你提到的晨跑还一起吗？')
            PrivateMessage.objects.create(conversation=conversation, sender=users[0], content='可以呀，明天早上七点操场见。')

        self.stdout.write(self.style.SUCCESS('演示数据已重建完成。'))
