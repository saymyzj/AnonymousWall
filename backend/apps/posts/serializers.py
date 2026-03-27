from rest_framework import serializers
from .models import Announcement, Poll, PollOption, PollVote, Post, PostImage
from apps.users.serializers import AnonymousIdentitySerializer


class PostImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ['id', 'image_url', 'thumbnail_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_thumbnail_url(self, obj):
        if not obj.thumbnail:
            return self.get_image_url(obj)
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url


class PollOptionSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = PollOption
        fields = ['id', 'text', 'vote_count', 'percentage']

    def get_percentage(self, obj):
        total = sum(option.vote_count for option in obj.poll.options.all()) or 1
        return round((obj.vote_count / total) * 100, 1)


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    has_voted = serializers.SerializerMethodField()
    selected_option_id = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ['id', 'question', 'expire_days', 'options', 'has_voted', 'selected_option_id']

    def get_has_voted(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and PollVote.objects.filter(poll=obj, user=request.user).exists())

    def get_selected_option_id(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = PollVote.objects.filter(poll=obj, user=request.user).first()
            return vote.option_id if vote else None
        return None


class PostListSerializer(serializers.ModelSerializer):
    identity = AnonymousIdentitySerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    has_poll = serializers.SerializerMethodField()
    moderation_label = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'identity', 'content_preview', 'tag', 'bg_color',
            'like_count', 'comment_count', 'favorite_count', 'created_at',
            'is_liked', 'is_favorited', 'is_author', 'is_pinned', 'images', 'has_poll',
            'status', 'moderation_reason', 'moderation_source', 'risk_level', 'review_deadline', 'moderation_label',
        ]

    def get_content_preview(self, obj):
        if len(obj.content) > 100:
            return obj.content[:100] + '...'
        return obj.content

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.interactions.models import Like
            return Like.objects.filter(
                user=request.user, target_type='post', target_id=obj.id
            ).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.interactions.models import Favorite
            return Favorite.objects.filter(
                user=request.user, target_type='post', target_id=obj.id
            ).exists()
        return False

    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False

    def get_has_poll(self, obj):
        return hasattr(obj, 'poll')

    def get_moderation_label(self, obj):
        if obj.status == 'rejected':
            return f'违规：{obj.moderation_reason or obj.ai_reason or "内容不符合社区规范"}'
        if obj.status == 'ai_suspect':
            risk_map = {
                'high': '高风险待复核',
                'medium': '中风险待复核',
                'low': '低风险待复核',
                'none': '待复核',
            }
            return risk_map.get(obj.risk_level, '待复核')
        if obj.status == 'pending':
            return '待人工审核'
        return ''


class PostDetailSerializer(serializers.ModelSerializer):
    identity = AnonymousIdentitySerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    poll = PollSerializer(read_only=True)
    moderation_label = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'identity', 'content', 'tag', 'bg_color',
            'like_count', 'comment_count', 'favorite_count',
            'created_at', 'updated_at', 'is_liked', 'is_favorited', 'is_author',
            'allow_messages', 'destroy_after_hours', 'is_pinned', 'images', 'poll',
            'status', 'moderation_reason', 'moderation_source', 'risk_level', 'review_deadline', 'moderation_label',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.interactions.models import Like
            return Like.objects.filter(
                user=request.user, target_type='post', target_id=obj.id
            ).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.interactions.models import Favorite
            return Favorite.objects.filter(
                user=request.user, target_type='post', target_id=obj.id
            ).exists()
        return False

    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False

    def get_moderation_label(self, obj):
        if obj.status == 'rejected':
            return f'违规：{obj.moderation_reason or obj.ai_reason or "内容不符合社区规范"}'
        if obj.status == 'ai_suspect':
            risk_map = {
                'high': '高风险待复核',
                'medium': '中风险待复核',
                'low': '低风险待复核',
                'none': '待复核',
            }
            return risk_map.get(obj.risk_level, '待复核')
        if obj.status == 'pending':
            return '待人工审核'
        return ''


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content', 'tag', 'bg_color', 'allow_messages', 'destroy_after_hours']

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError('内容不能为空')
        if len(value) > 500:
            raise serializers.ValidationError('内容不能超过500字')
        return value

    def validate_tag(self, value):
        valid_tags = [t[0] for t in Post.TAG_CHOICES]
        if value not in valid_tags:
            raise serializers.ValidationError(f'标签必须是以下之一: {", ".join(valid_tags)}')
        return value

    def validate_bg_color(self, value):
        if value not in range(1, 9):
            raise serializers.ValidationError('背景色编号必须在1-8之间')
        return value


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'start_at', 'end_at', 'created_at']
