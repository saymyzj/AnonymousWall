from django.db.models import Count
from django.utils import timezone

from apps.comments.models import Comment
from apps.interactions.models import Favorite, Like

from .models import Post


def build_tag_scores(user):
    tag_scores = {choice[0]: 0 for choice in Post.TAG_CHOICES}
    if not user or not user.is_authenticated:
        return tag_scores

    liked = Like.objects.filter(user=user, target_type='post').values('target_id')
    liked_posts = Post.objects.filter(pk__in=liked).values('tag').annotate(total=Count('id'))
    for row in liked_posts:
        tag_scores[row['tag']] += row['total'] * 2

    favorited = Favorite.objects.filter(user=user, target_type='post').values('target_id')
    favorite_posts = Post.objects.filter(pk__in=favorited).values('tag').annotate(total=Count('id'))
    for row in favorite_posts:
        tag_scores[row['tag']] += row['total'] * 3

    commented = Comment.objects.filter(author=user).values('post__tag').annotate(total=Count('id'))
    for row in commented:
        tag_scores[row['post__tag']] += row['total'] * 3

    return tag_scores


def score_post(post, tag_scores, now=None):
    now = now or timezone.now()
    hot = post.like_count * 2 + post.comment_count * 3 + post.favorite_count
    age_hours = max((now - post.created_at).total_seconds() / 3600, 0)
    time_score = 1 / (1 + age_hours / 24)
    tag_score = tag_scores.get(post.tag, 0)
    pin_bonus = 2 if post.is_pinned and (not post.pinned_until or post.pinned_until > now) else 0
    total = (tag_score * 0.4) + (hot * 0.3) + (time_score * 100 * 0.3) + pin_bonus
    return {
        'total': round(total, 2),
        'hot': hot,
        'time_score': round(time_score * 100, 2),
        'tag_score': tag_score,
        'pin_bonus': pin_bonus,
    }


def get_recommendation_snapshot(user=None, limit=10):
    candidates = [
        post for post in Post.objects.filter(
            is_deleted=False,
            status__in=['normal', 'ai_suspect'],
        ).select_related('identity').order_by('-created_at')
        if not post.is_expired
    ]

    if not user:
        return {
            'selected_user': None,
            'tag_scores': build_tag_scores(None),
            'posts': [],
        }

    tag_scores = build_tag_scores(user)
    now = timezone.now()
    rows = []
    for post in candidates[:50]:
        score = score_post(post, tag_scores, now=now)
        rows.append({
            'id': post.id,
            'content': post.content[:80] + ('...' if len(post.content) > 80 else ''),
            'tag': post.tag,
            'created_at': post.created_at,
            'score': score['total'],
            'hot': score['hot'],
            'time_score': score['time_score'],
            'tag_score': score['tag_score'],
            'pin_bonus': score['pin_bonus'],
            'link': f'/admin/posts/post/{post.id}/change/',
        })

    rows.sort(key=lambda item: item['score'], reverse=True)
    return {
        'selected_user': user,
        'tag_scores': sorted(tag_scores.items(), key=lambda item: item[1], reverse=True),
        'posts': rows[:limit],
        'formula': [
            '标签偏好分 = 点赞标签 * 2 + 收藏标签 * 3 + 评论标签 * 3',
            '热度分 = 点赞 * 2 + 评论 * 3 + 收藏 * 1',
            '时间分 = 1 / (1 + 帖子年龄小时 / 24) ，再乘以 100',
            '总分 = 标签偏好 * 0.4 + 热度 * 0.3 + 时间分 * 0.3 + 置顶加成',
        ],
    }
