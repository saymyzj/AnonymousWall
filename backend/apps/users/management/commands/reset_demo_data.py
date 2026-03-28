from collections import Counter, defaultdict
from datetime import timedelta
import random

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.comments.models import Comment
from apps.interactions.models import Conversation, Favorite, Like, Notification, PrivateMessage, Report
from apps.moderation.models import AuditLog, SensitiveWord
from apps.posts.models import Announcement, Poll, PollOption, PollVote, Post
from apps.users.models import AnonymousIdentity, User
from apps.users.utils import generate_avatar_seed, generate_nickname


class Command(BaseCommand):
    help = '清空数据库并生成更大规模、更接近真实使用习惯的演示数据'

    USER_COUNT = 240
    POST_COUNT = 1200
    TAGS = [choice[0] for choice in Post.TAG_CHOICES]
    SURNAMES = list('赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜')
    GIVEN_NAMES = [
        '一诺', '安然', '白露', '博文', '晨曦', '初夏', '从容', '丹宁', '冬晴', '飞扬', '芙蓉', '海宁',
        '嘉禾', '嘉言', '静姝', '景澄', '景行', '可心', '乐天', '明远', '沐言', '南栀', '若溪', '思齐',
        '书禾', '听雨', '宛晴', '文博', '溪宁', '向晚', '星野', '雅宁', '奕辰', '以沫', '语汐', '昭宁',
    ]
    POST_TOPICS = {
        '表白': {
            'openings': ['想认真夸一下', '忍不住想表白', '今天又被打动了', '想把这份心动写下来'],
            'subjects': ['图书馆靠窗背单词的同学', '总是顺手帮大家扶门的人', '雨天把伞借给陌生人的学姐', '排练厅里弹钢琴的那位同学'],
            'details': ['笑起来特别治愈', '说话温温柔柔却很有力量', '认真做事的时候非常耀眼', '把善意落在了很多小细节里'],
            'closings': ['如果你看到，希望你今天也有好心情', '只想把喜欢说出来，不打扰你的生活', '愿这条匿名小纸条能被风带到你身边', '谢谢你让校园里多了一点光'],
        },
        '吐槽': {
            'openings': ['真的想吐槽一下', '今天被折腾得有点无语', '想在这里发泄三分钟', '必须记录一下这波心累'],
            'subjects': ['宿舍楼半夜的外放音乐', '早八前排队失败的早餐窗口', '临时改时间的小组作业讨论', '反复拖延又突然催命的课程通知'],
            'details': ['完全打乱了今天的节奏', '让人瞬间失去情绪管理', '明明可以提前沟通却偏偏最后一刻', '对普通同学真的太不友好了'],
            'closings': ['希望明天一切顺一点', '有同感的朋友欢迎抱团取暖', '写出来之后气消了一半', '也欢迎大家分享更优雅的解决方法'],
        },
        '求助': {
            'openings': ['想认真求助一下', '卡在这里已经有点慌了', '来这里碰碰运气', '希望有经验的同学能指点一下'],
            'subjects': ['数据结构最后一道题', '保研材料准备节奏', '跨专业选修课入门方法', '实习面试前的项目梳理'],
            'details': ['自己查了资料但还是没完全理顺', '担心走错方向浪费时间', '想找更高效的学习路径', '希望少踩一些前人踩过的坑'],
            'closings': ['如果方便的话拜托留言', '真的会非常感谢', '也欢迎私信我分享经验', '先在这里谢过大家了'],
        },
        '树洞': {
            'openings': ['想把今天的情绪丢进树洞', '只是想安静说几句', '最近有点需要一个出口', '写给不认识的你们'],
            'subjects': ['对未来的不确定感', '和朋友之间微妙的距离感', '努力之后仍然焦虑的状态', '一个人吃饭时突然涌上的孤独感'],
            'details': ['没有具体的大事，却一直闷闷的', '表面上看都正常，心里却总有点悬着', '好像每个人都在奔跑，我却时快时慢', '明明在校园里，却偶尔觉得自己像个旁观者'],
            'closings': ['写出来之后轻了一点', '希望明天会更稳一点', '谢谢看到这里的陌生人', '也祝你今晚能睡个好觉'],
        },
        '失物招领': {
            'openings': ['失物招领一下', '帮忙扩散一条', '今天路上捡到', '在教学楼附近发现'],
            'subjects': ['一把黑色折叠伞', '一本写了课程笔记的活页本', '一个蓝牙耳机充电盒', '一张饭卡和校园卡套'],
            'details': ['地点在图书馆三楼靠近打印区', '是在操场看台第二排附近看到的', '东西已经先替失主保管起来了', '可以描述一下细节来确认领取'],
            'closings': ['希望尽快物归原主', '转发给可能认识失主的朋友也行', '失主私信我就好', '如果今天认领不到，明天会交到失物处'],
        },
        '搭子': {
            'openings': ['认真找个搭子', '想在这里捞一下同频伙伴', '来招募一个稳定搭子', '如果你也在找人一起'],
            'subjects': ['晨跑打卡', '晚间自习', '英语口语练习', '周末看展或逛校园周边'],
            'details': ['希望节奏稳定、彼此不放鸽子', '最好能互相提醒和监督', '新手也完全可以一起慢慢来', '比起厉害，更想找能长期坚持的人'],
            'closings': ['感兴趣可以留言聊聊', '时间地点都可以再商量', '希望在这里遇到靠谱搭子', '一个人坚持太难了，想试试结伴'],
        },
    }
    COMMENT_TOPICS = {
        '表白': ['我也注意到过这个人，真的很有感染力', '这样的心动好真诚，祝你今天顺利', '读完有点被治愈，校园需要这种温柔', '如果我是对方，看到一定会开心'],
        '吐槽': ['太真实了，我也被同样的事情折磨过', '建议先保留证据，必要时真的要反馈', '写得我狠狠共鸣了，今天也很心累', '先抱抱你，确实很影响日常状态'],
        '求助': ['我之前也是这么过来的，可以先从这个角度试试', '建议把问题拆成几个小块，会没那么慌', '这个方向是对的，关键在于先把基础概念捋顺', '如果你愿意，我可以分享我当时的资料清单'],
        '树洞': ['谢谢你愿意说出来，很多人都经历过这种阶段', '先别急着否定自己，能表达已经很不容易了', '希望你今晚先好好休息，明天再看世界会松一点', '你不是一个人，很多情绪都值得被认真看见'],
        '失物招领': ['帮你顶一下，希望失主快点看到', '可以顺便发到年级群里，效率会高一些', '好人一生平安，失主看到会很感激', '这种细节真的很加分，感谢你替别人留意'],
        '搭子': ['这个我有兴趣，可以交流一下时间安排', '建议先约一周试试节奏，合适再长期绑定', '我也在找同频搭子，感觉这个方向很不错', '一起打卡确实会更容易坚持，支持一下'],
    }
    REPLY_TOPICS = {
        '表白': ['这种细节真的很打动人，继续保持喜欢就很好', '如果你愿意慢慢接触，说不定会有回应', '能把喜欢表达出来已经很勇敢了', '这种真诚的喜欢很难得，祝你顺利'],
        '吐槽': ['这事确实离谱，换成我也会很烦', '最好先把过程记下来，后面更方便反馈', '先别让这件事影响到你整天心情', '碰到这种情况真的很需要一个出口'],
        '求助': ['你可以先把最卡的一步拆出来看', '这个方向没问题，再往前推一小步就会清楚很多', '如果时间紧，先保住基础分会更稳', '这种题通常卡在边界条件，先从例子入手会更快'],
        '树洞': ['能说出来已经很不容易了，先别逼自己立刻变好', '有时候只是最近太累，不一定是你真的不行', '先把今天过完就很好，剩下的明天再想', '这种阶段很多人都会有，别急着一个人扛'],
        '失物招领': ['我也帮你留意一下，看到类似信息会转给你', '可以再补一下颜色和位置，可能更容易找到失主', '这种信息发出来很有帮助，希望很快就能对上', '先替失主谢谢你，真的很暖心'],
        '搭子': ['听起来挺靠谱的，关键还是节奏要能对上', '如果时间能固定下来，长期坚持会容易很多', '这种目标最好先试一周，合适再继续', '我觉得先把频率约好，后面会省很多沟通成本'],
    }
    MESSAGE_TOPICS = [
        '你好，我对你这条内容挺有共鸣的，想继续聊聊。',
        '看到你的帖子后想来确认一下细节，方便的话回复我一下。',
        '我也想一起参与，如果你还在找人可以继续联系。',
        '这件事我可能帮得上忙，有需要的话我可以补充一点经验。',
    ]
    REPORT_REASONS = ['广告引流', '人身攻击', '色情低俗', '隐私泄露', '其他']
    POST_REPORT_DETAILS = [
        '这条内容的措辞有点过线，建议管理员看一下。',
        '感觉这段话容易引起争执，担心继续扩散。',
        '里面有明显的不当表述，可能会影响社区氛围。',
        '这条内容看着不太合适，麻烦帮忙判断一下。',
    ]
    COMMENT_REPORT_DETAILS = [
        '这条评论语气有些冲，可能会带偏讨论。',
        '评论内容让我不太舒服，建议人工确认一下。',
        '这条回复有点像在针对人，怕后面越吵越大。',
        '感觉这条评论不太合适，想请管理员看看。',
    ]

    def handle(self, *args, **options):
        self.rng = random.Random(20260328)
        self.now = timezone.now()
        self.stdout.write('开始清空数据库...')
        call_command('flush', interactive=False, verbosity=0)

        self._create_sensitive_words()
        admin_user = self._create_admin_user()
        self.admin_user = admin_user
        users, preferences = self._create_users()
        identity_map = self._create_identities(users)
        posts, posts_by_tag = self._create_posts(users, preferences, identity_map)
        comments, comments_by_tag = self._create_comments(posts, users, preferences, identity_map)
        self._create_polls(posts, users)
        self._create_interactions(posts, comments, users, preferences, posts_by_tag, comments_by_tag)
        self._create_reports_and_audits(posts, comments, users)
        self._create_conversations(posts, users)
        self._create_announcements(posts)

        self.stdout.write(self.style.SUCCESS(
            f'数据重建完成：admin={admin_user.email} / password=admin，用户 {User.objects.filter(is_staff=False).count()}，'
            f'帖子 {Post.objects.count()}，评论 {Comment.objects.count()}，点赞 {Like.objects.count()}，收藏 {Favorite.objects.count()}。'
        ))

    def _create_sensitive_words(self):
        words = [
            ('广告引流', 'soft'),
            ('代写代考', 'hard'),
            ('裸聊', 'hard'),
            ('刷单兼职', 'hard'),
            ('买卖证件', 'hard'),
            ('私下加群', 'soft'),
            ('低价转让链接', 'soft'),
            ('外网资源', 'soft'),
            ('威胁辱骂', 'soft'),
            ('人肉搜索', 'hard'),
        ]
        for word, level in words:
            SensitiveWord.objects.create(word=word, level=level)

    def _create_admin_user(self):
        return User.objects.create_superuser(
            email='Admin',
            password='admin',
            real_name='Admin',
            student_id='ADMIN',
            is_verified=True,
        )

    def _create_users(self):
        users = []
        preferences = {}
        for index in range(self.USER_COUNT):
            verified = index >= 24
            banned = verified and index % 19 == 0 and index < 96
            user = User.objects.create_user(
                email=f'user{index + 1:03d}@example.com',
                password='Demo123456',
                real_name=self._build_name(index),
                student_id=f'2026{index + 1:04d}',
                is_verified=verified,
                is_banned=banned,
                ban_until=self.now + timedelta(days=self.rng.choice([3, 7, 15, 30])) if banned else None,
            )
            preferences[user.id] = self.rng.sample(self.TAGS, 2)
            users.append(user)
        return users, preferences

    def _create_identities(self, users):
        identity_map = defaultdict(list)
        for user in users:
            for offset in range(self.rng.randint(2, 3)):
                identity = AnonymousIdentity.objects.create(
                    user=user,
                    nickname=generate_nickname(),
                    avatar_seed=generate_avatar_seed(),
                )
                identity_map[user.id].append(identity)
        return identity_map

    def _create_posts(self, users, preferences, identity_map):
        posts = []
        post_times = []
        posts_by_tag = defaultdict(list)
        verified_users = [user for user in users if user.is_verified]
        users_by_tag = {
            tag: [user for user in verified_users if tag in preferences[user.id]]
            for tag in self.TAGS
        }
        for index in range(self.POST_COUNT):
            tag = self.TAGS[index % len(self.TAGS)]
            author_pool = users_by_tag[tag] or verified_users
            author = self.rng.choice(author_pool if self.rng.random() < 0.78 else verified_users)
            identity = self.rng.choice(identity_map[author.id])
            created_at = self._recent_datetime()
            status = self._post_status_for(index)
            payload = self._post_status_payload(status, created_at)
            post = Post(
                author=author,
                identity=identity,
                content=self._build_post_content(tag, index),
                tag=tag,
                bg_color=self.rng.randint(1, 8),
                allow_messages=self.rng.random() < 0.72,
                destroy_after_hours=24 if tag == '树洞' and self.rng.random() < 0.12 else None,
                created_at=created_at,
                updated_at=created_at + timedelta(hours=self.rng.randint(0, 36)),
                **payload,
            )
            posts.append(post)
            post_times.append((created_at, post.updated_at))
        Post.objects.bulk_create(posts, batch_size=200)
        posts = list(Post.objects.select_related('author', 'identity').order_by('id'))
        for post, (created_at, updated_at) in zip(posts, post_times):
            post.created_at = created_at
            post.updated_at = updated_at
        Post.objects.bulk_update(posts, ['created_at', 'updated_at'], batch_size=200)

        pinned_candidates = [post for post in posts if post.status == 'normal'][:12]
        for post in pinned_candidates:
            post.is_pinned = True
            post.pinned_until = self.now + timedelta(days=self.rng.randint(3, 10))
        Post.objects.bulk_update(pinned_candidates, ['is_pinned', 'pinned_until'])

        for post in posts:
            posts_by_tag[post.tag].append(post)
        return posts, posts_by_tag

    def _create_comments(self, posts, users, preferences, identity_map):
        comments = []
        comments_by_tag = defaultdict(list)
        active_users = [user for user in users if user.is_verified]
        users_by_tag = {
            tag: [user for user in active_users if tag in preferences[user.id]]
            for tag in self.TAGS
        }

        for index, post in enumerate(posts):
            base_count = self.rng.randint(1, 5)
            if index % 5 == 0:
                base_count += 2
            post_comments = []
            for number in range(base_count):
                author = self.rng.choice(users_by_tag[post.tag] or active_users)
                identity = self.rng.choice(identity_map[author.id])
                status = self._comment_status_for(index, number)
                comment_created_at = self._comment_datetime(post.created_at)
                comment = Comment.objects.create(
                    post=post,
                    author=author,
                    identity=identity,
                    parent=None,
                    content=self._build_comment_content(post.tag, number),
                    **self._comment_status_payload(status),
                )
                Comment.objects.filter(pk=comment.pk).update(created_at=comment_created_at)
                comment.created_at = comment_created_at
                comments.append(comment)
                comments_by_tag[post.tag].append(comment)
                post_comments.append(comment)

            reply_total = self.rng.randint(0, max(1, base_count // 2))
            for reply_index in range(reply_total):
                parent = self.rng.choice(post_comments)
                author = self.rng.choice(users_by_tag[post.tag] or active_users)
                identity = self.rng.choice(identity_map[author.id])
                status = self._comment_status_for(index, base_count + reply_index, reply=True)
                comment_created_at = self._reply_datetime(parent.created_at)
                comment = Comment.objects.create(
                    post=post,
                    author=author,
                    identity=identity,
                    parent=parent,
                    content=self._build_comment_content(post.tag, reply_index, reply=True),
                    **self._comment_status_payload(status),
                )
                Comment.objects.filter(pk=comment.pk).update(created_at=comment_created_at)
                comment.created_at = comment_created_at
                comments.append(comment)
                comments_by_tag[post.tag].append(comment)
                post_comments.append(comment)

        return comments, comments_by_tag

    def _create_polls(self, posts, users):
        candidates = [post for post in posts if post.status == 'normal' and post.tag in {'求助', '吐槽', '搭子', '表白'}][:120]
        poll_votes = []
        option_updates = []
        for index, post in enumerate(candidates):
            poll = Poll.objects.create(
                post=post,
                question=self._build_poll_question(post.tag, index),
                expire_days=self.rng.choice([1, 3, 7]),
            )
            option_texts = self._build_poll_options(post.tag)
            options = [
                PollOption(poll=poll, text=text, vote_count=0)
                for text in option_texts
            ]
            PollOption.objects.bulk_create(options)
            options = list(poll.options.all())
            voters = self.rng.sample(users, k=min(len(users), self.rng.randint(16, 48)))
            for voter in voters:
                option = self.rng.choice(options)
                poll_votes.append(PollVote(
                    poll=poll,
                    option=option,
                    user=voter,
                    created_at=self.now - timedelta(days=self.rng.randint(0, 120), hours=self.rng.randint(0, 23)),
                ))
                option.vote_count += 1
            option_updates.extend(options)
        if poll_votes:
            PollVote.objects.bulk_create(poll_votes, batch_size=500)
        if option_updates:
            PollOption.objects.bulk_update(option_updates, ['vote_count'], batch_size=200)

    def _create_interactions(self, posts, comments, users, preferences, posts_by_tag, comments_by_tag):
        visible_posts = [post for post in posts if post.status in {'normal', 'ai_suspect'} and not post.is_deleted]
        visible_comments = [comment for comment in comments if comment.status in {'normal', 'ai_suspect'}]
        visible_posts_by_tag = {
            tag: [post for post in items if post.status in {'normal', 'ai_suspect'} and not post.is_deleted]
            for tag, items in posts_by_tag.items()
        }
        visible_comments_by_tag = {
            tag: [comment for comment in items if comment.status in {'normal', 'ai_suspect'}]
            for tag, items in comments_by_tag.items()
        }

        post_like_counts = Counter()
        post_favorite_counts = Counter()
        comment_like_counts = Counter()
        notifications = []
        likes = []
        favorites = []
        comment_like_keys = set()
        post_like_keys = set()
        favorite_keys = set()

        for user in users:
            preferred = preferences[user.id]
            post_pool = self._blend_posts(visible_posts_by_tag, visible_posts, preferred)
            liked_posts = self._sample_without_own_posts(post_pool, user.id, self.rng.randint(16, 32))
            for post in liked_posts:
                key = (user.id, post.id)
                if key in post_like_keys:
                    continue
                post_like_keys.add(key)
                likes.append(Like(
                    user=user,
                    target_type='post',
                    target_id=post.id,
                    created_at=self.now - timedelta(days=self.rng.randint(0, 90), hours=self.rng.randint(0, 23)),
                ))
                post_like_counts[post.id] += 1
                if post.author_id != user.id and self.rng.random() < 0.38:
                    notifications.append(self._notification(
                        user=post.author,
                        type_='like',
                        title='你的帖子收到了新的点赞',
                        content=f'你的「{post.tag}」帖子又被点了个赞。',
                        link=f'/post/{post.id}',
                    ))

            favorite_count = self.rng.randint(1, min(12, len(liked_posts))) if liked_posts else 0
            for post in liked_posts[:favorite_count]:
                key = (user.id, post.id)
                if key in favorite_keys:
                    continue
                favorite_keys.add(key)
                favorites.append(Favorite(
                    user=user,
                    target_type='post',
                    target_id=post.id,
                    created_at=self.now - timedelta(days=self.rng.randint(0, 90), hours=self.rng.randint(0, 23)),
                ))
                post_favorite_counts[post.id] += 1
                if post.author_id != user.id and self.rng.random() < 0.62:
                    notifications.append(self._notification(
                        user=post.author,
                        type_='favorite',
                        title='你的帖子被加入收藏',
                        content=f'有人收藏了你的「{post.tag}」帖子。',
                        link=f'/post/{post.id}',
                    ))

            comment_pool = self._blend_comments(visible_comments_by_tag, visible_comments, preferred)
            liked_comments = self._sample_without_own_comments(comment_pool, user.id, self.rng.randint(10, 24))
            for comment in liked_comments:
                key = (user.id, comment.id)
                if key in comment_like_keys:
                    continue
                comment_like_keys.add(key)
                likes.append(Like(
                    user=user,
                    target_type='comment',
                    target_id=comment.id,
                    created_at=self.now - timedelta(days=self.rng.randint(0, 90), hours=self.rng.randint(0, 23)),
                ))
                comment_like_counts[comment.id] += 1
                if comment.author_id != user.id and self.rng.random() < 0.28:
                    notifications.append(self._notification(
                        user=comment.author,
                        type_='like',
                        title='你的评论收到了新的点赞',
                        content='有人为你的一条评论点了赞。',
                        link=f'/post/{comment.post_id}#comments',
                    ))

        for comment in comments:
            if comment.author_id != comment.post.author_id and comment.status in {'normal', 'ai_suspect'} and self.rng.random() < 0.72:
                notifications.append(self._notification(
                    user=comment.post.author,
                    type_='comment',
                    title='你的帖子收到了一条新评论',
                    content=comment.content[:90],
                    link=f'/post/{comment.post_id}#comments',
                ))

        if likes:
            Like.objects.bulk_create(likes, batch_size=1000)
        if favorites:
            Favorite.objects.bulk_create(favorites, batch_size=500)

        for post in posts:
            post.like_count = post_like_counts.get(post.id, 0)
            post.favorite_count = post_favorite_counts.get(post.id, 0)
            post.comment_count = post.comments.filter(status__in=['normal', 'ai_suspect']).count()
        Post.objects.bulk_update(posts, ['like_count', 'favorite_count', 'comment_count'], batch_size=200)

        for comment in comments:
            comment.like_count = comment_like_counts.get(comment.id, 0)
        Comment.objects.bulk_update(comments, ['like_count'], batch_size=500)

        system_notifications = []
        for user in users[:80]:
            system_notifications.append(self._notification(
                user=user,
                type_='system',
                title='欢迎来到 匿名宇宙',
                content='这里刚刚更新了一批新的校园动态，看看首页或推荐页有没有你感兴趣的话题。',
                link='/',
            ))
        Notification.objects.bulk_create(notifications + system_notifications, batch_size=1000)

    def _create_reports_and_audits(self, posts, comments, users):
        content_reports = []
        audit_logs = []
        notifications = []
        risky_posts = [post for post in posts if post.status in {'rejected', 'pending', 'ai_suspect'}][:120]
        risky_comments = [comment for comment in comments if comment.status in {'rejected', 'pending', 'ai_suspect'}][:160]

        for post in risky_posts:
            reporter_count = self.rng.randint(1, 3)
            reporters = self.rng.sample([user for user in users if user.id != post.author_id], k=reporter_count)
            for reporter in reporters:
                status = self.rng.choices(['pending', 'resolved', 'ignored'], weights=[3, 4, 2], k=1)[0]
                content_reports.append(Report(
                    user=reporter,
                    target_type='post',
                    target_id=post.id,
                    reason=self.rng.choice(self.REPORT_REASONS),
                    detail=self.rng.choice(self.POST_REPORT_DETAILS),
                    status=status,
                    created_at=self.now - timedelta(days=self.rng.randint(0, 60), hours=self.rng.randint(0, 23)),
                ))
            if post.status == 'rejected':
                audit_logs.append(AuditLog(
                    auditor=self.admin_user,
                    target_type='post',
                    target_id=post.id,
                    action='reject',
                    reason=post.moderation_reason or '内容存在较高风险，已下架处理',
                    created_at=self.now - timedelta(days=self.rng.randint(0, 45), hours=self.rng.randint(0, 23)),
                ))
                notifications.append(self._notification(
                    user=post.author,
                    type_='system',
                    title='你的帖子已被管理员下架',
                    content=post.moderation_reason or '内容存在较高风险，当前已被下架。',
                    link='/profile',
                ))

        for comment in risky_comments:
            reporter_count = self.rng.randint(1, 2)
            reporters = self.rng.sample([user for user in users if user.id != comment.author_id], k=reporter_count)
            for reporter in reporters:
                status = self.rng.choices(['pending', 'resolved', 'ignored'], weights=[3, 4, 2], k=1)[0]
                content_reports.append(Report(
                    user=reporter,
                    target_type='comment',
                    target_id=comment.id,
                    reason=self.rng.choice(self.REPORT_REASONS),
                    detail=self.rng.choice(self.COMMENT_REPORT_DETAILS),
                    status=status,
                    created_at=self.now - timedelta(days=self.rng.randint(0, 60), hours=self.rng.randint(0, 23)),
                ))
            if comment.status == 'rejected':
                audit_logs.append(AuditLog(
                    auditor=self.admin_user,
                    target_type='comment',
                    target_id=comment.id,
                    action='reject',
                    reason=comment.moderation_reason or '评论存在争议表达，已下架处理',
                    created_at=self.now - timedelta(days=self.rng.randint(0, 45), hours=self.rng.randint(0, 23)),
                ))

        banned_users = list(User.objects.filter(is_banned=True))
        for user in banned_users:
            audit_logs.append(AuditLog(
                auditor=self.admin_user,
                target_type='user',
                target_id=user.id,
                action='ban',
                reason=f'多次收到有效举报，禁言至 {user.ban_until.strftime("%Y-%m-%d") if user.ban_until else "永久"}',
                created_at=self.now - timedelta(days=self.rng.randint(0, 30), hours=self.rng.randint(0, 23)),
            ))
            notifications.append(self._notification(
                user=user,
                type_='system',
                title='你的账号处于禁言状态',
                content='因近期多次出现争议内容，账号暂时受到禁言处理，请留意后续通知。',
                link='/profile',
            ))

        if content_reports:
            Report.objects.bulk_create(content_reports, batch_size=500)
        if audit_logs:
            AuditLog.objects.bulk_create(audit_logs, batch_size=300)
        if notifications:
            Notification.objects.bulk_create(notifications, batch_size=300)

    def _create_conversations(self, posts, users):
        admin_user = User.objects.get(email='Admin')
        message_notifications = []
        conversation_candidates = [post for post in posts if post.allow_messages and post.status == 'normal'][:180]
        for index, post in enumerate(conversation_candidates):
            participant_pool = [user for user in users if user.id != post.author_id]
            if not participant_pool:
                continue
            participant = self.rng.choice(participant_pool)
            conversation = Conversation.objects.create(
                post=post,
                owner=post.author,
                participant=participant,
                is_blocked=index % 37 == 0,
            )
            sender = participant
            for round_index in range(self.rng.randint(2, 5)):
                PrivateMessage.objects.create(
                    conversation=conversation,
                    sender=sender,
                    content=self.MESSAGE_TOPICS[(index + round_index) % len(self.MESSAGE_TOPICS)],
                    is_read=round_index < 2,
                )
                receiver = post.author if sender.id == participant.id else participant
                if receiver != admin_user and self.rng.random() < 0.45:
                    message_notifications.append(self._notification(
                        user=receiver,
                        type_='message',
                        title='你收到一条新的匿名私信',
                        content='有人在消息中心给你发来了一条新的匿名私信。',
                        link=f'/messages?tab=messages&conversation={conversation.id}',
                    ))
                sender = post.author if sender.id == participant.id else participant
        if message_notifications:
            Notification.objects.bulk_create(message_notifications, batch_size=300)

    def _create_announcements(self, posts):
        Announcement.objects.create(
            title='本周校园热议话题已更新',
            content='首页和推荐页会持续出现新的校园话题，欢迎按标签浏览或直接参与讨论。',
            is_active=True,
            start_at=self.now - timedelta(hours=2),
            end_at=self.now + timedelta(days=10),
        )
        Announcement.objects.create(
            title='互动越多，推荐越懂你',
            content='点赞、收藏和评论都会影响推荐排序，想看到更多同类内容可以多参与互动。',
            is_active=True,
            start_at=self.now - timedelta(days=1),
            end_at=self.now + timedelta(days=14),
        )
        Announcement.objects.create(
            title='消息中心功能说明',
            content='评论提醒、点赞提醒和私信通知都会在消息中心汇总展示，记得及时查看。',
            is_active=True,
            start_at=self.now - timedelta(hours=1),
            end_at=self.now + timedelta(days=7),
        )

        recent_posts = [post for post in posts if post.status == 'normal'][:24]
        for post in recent_posts:
            Notification.objects.create(
                user=post.author,
                type='system',
                title='你的帖子正在获得更多曝光',
                content='最近有更多用户浏览和互动你的帖子，记得留意评论区的新消息。',
                link=f'/post/{post.id}',
            )

    def _build_name(self, index):
        surname = self.SURNAMES[index % len(self.SURNAMES)]
        given = self.GIVEN_NAMES[(index * 5) % len(self.GIVEN_NAMES)]
        return f'{surname}{given}'

    def _recent_datetime(self):
        day_index = self.rng.choices(
            population=[0, 1, 2, 3, 4, 5, 6],
            weights=[10, 14, 18, 20, 16, 12, 10],
            k=1,
        )[0]
        dt = self.now - timedelta(
            days=day_index,
            hours=self.rng.randint(0, 23),
            minutes=self.rng.randint(0, 59),
            seconds=self.rng.randint(0, 59),
        )
        return max(dt, self.now - timedelta(days=6, hours=23, minutes=59))

    def _comment_datetime(self, post_created_at):
        dt = post_created_at + timedelta(
            hours=self.rng.randint(0, 36),
            minutes=self.rng.randint(0, 59),
            seconds=self.rng.randint(0, 59),
        )
        return min(dt, self.now)

    def _reply_datetime(self, parent_created_at):
        dt = parent_created_at + timedelta(
            minutes=self.rng.randint(5, 360),
            seconds=self.rng.randint(0, 59),
        )
        return min(dt, self.now)

    def _post_status_for(self, index):
        if index % 43 == 0:
            return 'rejected'
        if index % 29 == 0:
            return 'pending'
        if index % 17 == 0:
            return 'ai_suspect'
        return 'normal'

    def _comment_status_for(self, post_index, comment_index, reply=False):
        marker = post_index + comment_index + (11 if reply else 0)
        if marker % 59 == 0:
            return 'rejected'
        if marker % 41 == 0:
            return 'pending'
        if marker % 23 == 0:
            return 'ai_suspect'
        return 'normal'

    def _post_status_payload(self, status, created_at):
        if status == 'rejected':
            return {
                'status': 'rejected',
                'moderation_source': 'manual',
                'moderation_reason': '内容包含较强攻击性表达，已下架处理',
                'ai_decision': 'reject',
                'ai_reason': '命中高风险表达模式',
                'risk_level': 'high',
                'review_deadline': None,
                'reviewed_at': created_at + timedelta(hours=3),
            }
        if status == 'pending':
            return {
                'status': 'pending',
                'moderation_source': 'ai',
                'moderation_reason': '内容表达边界较模糊，暂时进入人工审核',
                'ai_decision': 'confuse',
                'ai_reason': '语义存在歧义，建议人工进一步确认',
                'risk_level': 'medium',
                'review_deadline': created_at + timedelta(days=3),
                'reviewed_at': None,
            }
        if status == 'ai_suspect':
            return {
                'status': 'ai_suspect',
                'moderation_source': 'soft_word',
                'moderation_reason': '命中软标记词，需要人工复核',
                'ai_decision': 'not_run',
                'ai_reason': '命中软标记词，系统已转入人工复核',
                'risk_level': 'medium',
                'review_deadline': created_at + timedelta(days=5),
                'reviewed_at': None,
            }
        return {
            'status': 'normal',
            'moderation_source': 'ai',
            'moderation_reason': '内容正常',
            'ai_decision': 'accept',
            'ai_reason': '语义积极或中性，无违规风险',
            'risk_level': self.rng.choice(['none', 'low']),
            'review_deadline': None,
            'reviewed_at': created_at + timedelta(minutes=40),
        }

    def _comment_status_payload(self, status):
        if status == 'rejected':
            return {
                'status': 'rejected',
                'moderation_source': 'manual',
                'moderation_reason': '评论存在攻击性或挑衅表达，已下架处理',
                'ai_decision': 'reject',
                'ai_reason': '存在明显争议或攻击倾向',
                'risk_level': 'high',
                'review_deadline': None,
                'reviewed_at': self.now,
            }
        if status == 'pending':
            return {
                'status': 'pending',
                'moderation_source': 'ai',
                'moderation_reason': '评论表达存在争议，暂缓展示并进入人工审核',
                'ai_decision': 'confuse',
                'ai_reason': '上下文存在歧义，建议人工确认',
                'risk_level': 'medium',
                'review_deadline': self.now + timedelta(days=2),
                'reviewed_at': None,
            }
        if status == 'ai_suspect':
            return {
                'status': 'ai_suspect',
                'moderation_source': 'soft_word',
                'moderation_reason': '评论命中软标记词，需要人工复核',
                'ai_decision': 'not_run',
                'ai_reason': '命中软标记词，系统已转入人工复核',
                'risk_level': 'medium',
                'review_deadline': self.now + timedelta(days=3),
                'reviewed_at': None,
            }
        return {
            'status': 'normal',
            'moderation_source': 'ai',
            'moderation_reason': '内容正常',
            'ai_decision': 'accept',
            'ai_reason': '评论内容正常',
            'risk_level': self.rng.choice(['none', 'low']),
            'review_deadline': None,
            'reviewed_at': self.now,
        }

    def _build_post_content(self, tag, index):
        pool = self.POST_TOPICS[tag]
        opening = pool['openings'][index % len(pool['openings'])]
        subject = self.rng.choice(pool['subjects'])
        detail = self.rng.choice(pool['details'])
        closing = pool['closings'][(index // len(self.TAGS)) % len(pool['closings'])]
        return f'{opening}{subject}，{detail}。{closing}'

    def _build_comment_content(self, tag, index, reply=False):
        source = self.REPLY_TOPICS if reply else self.COMMENT_TOPICS
        text = source[tag][index % len(source[tag])]
        if reply:
            return text
        return text

    def _build_poll_question(self, tag, index):
        if tag == '求助':
            return f'如果你遇到类似情况，第 {index % 3 + 1} 步会先怎么做？'
        if tag == '搭子':
            return f'找搭子时你最看重哪一点？'
        if tag == '表白':
            return f'遇到心动的人，你通常会怎么表达？'
        return f'看到这类内容时，你第一反应更接近哪一种？'

    def _build_poll_options(self, tag):
        options_map = {
            '求助': ['先查资料', '问同学', '去找老师', '先睡一觉再说'],
            '搭子': ['时间稳定', '目标一致', '沟通舒服', '距离方便'],
            '表白': ['直接表达', '先慢慢接触', '写小纸条', '继续暗恋'],
            '吐槽': ['立刻反馈', '先忍一忍', '找朋友吐槽', '记录下来复盘'],
        }
        return options_map.get(tag, ['非常同意', '还行', '一般般', '不太认同'])[:self.rng.randint(2, 4)]

    def _blend_posts(self, posts_by_tag, fallback_posts, preferred_tags):
        primary = list(posts_by_tag.get(preferred_tags[0], []))
        secondary = list(posts_by_tag.get(preferred_tags[1], []))
        extra = list(fallback_posts)
        self.rng.shuffle(primary)
        self.rng.shuffle(secondary)
        self.rng.shuffle(extra)
        return primary[:120] + secondary[:90] + extra[:140]

    def _blend_comments(self, comments_by_tag, fallback_comments, preferred_tags):
        primary = list(comments_by_tag.get(preferred_tags[0], []))
        secondary = list(comments_by_tag.get(preferred_tags[1], []))
        extra = list(fallback_comments)
        self.rng.shuffle(primary)
        self.rng.shuffle(secondary)
        self.rng.shuffle(extra)
        return primary[:140] + secondary[:110] + extra[:150]

    def _sample_without_own_posts(self, posts, user_id, target_count):
        filtered = [post for post in posts if post.author_id != user_id]
        if not filtered:
            return []
        sample_size = min(len(filtered), target_count)
        return self.rng.sample(filtered, sample_size)

    def _sample_without_own_comments(self, comments, user_id, target_count):
        filtered = [comment for comment in comments if comment.author_id != user_id]
        if not filtered:
            return []
        sample_size = min(len(filtered), target_count)
        return self.rng.sample(filtered, sample_size)

    def _notification(self, user, type_, title, content, link):
        return Notification(
            user=user,
            type=type_,
            title=title[:120],
            content=content[:300],
            link=link,
            is_read=self.rng.random() < 0.58,
            is_ignored=False,
            created_at=self.now - timedelta(days=self.rng.randint(0, 45), hours=self.rng.randint(0, 23)),
        )
