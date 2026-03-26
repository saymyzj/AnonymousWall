from rest_framework import serializers
from .models import Post
from apps.users.serializers import AnonymousIdentitySerializer


class PostListSerializer(serializers.ModelSerializer):
    identity = AnonymousIdentitySerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'identity', 'content_preview', 'tag', 'bg_color',
            'like_count', 'comment_count', 'favorite_count', 'created_at',
            'is_liked', 'is_author',
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

    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False


class PostDetailSerializer(serializers.ModelSerializer):
    identity = AnonymousIdentitySerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'identity', 'content', 'tag', 'bg_color',
            'like_count', 'comment_count', 'favorite_count',
            'created_at', 'updated_at', 'is_liked', 'is_author',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.interactions.models import Like
            return Like.objects.filter(
                user=request.user, target_type='post', target_id=obj.id
            ).exists()
        return False

    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content', 'tag', 'bg_color']

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
