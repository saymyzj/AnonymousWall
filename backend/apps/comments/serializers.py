from rest_framework import serializers
from .models import Comment


ANON_LABELS = ['匿名A', '匿名B', '匿名C', '匿名D', '匿名E', '匿名F', '匿名G', '匿名H']
ANON_COLORS = ['#7C5CFC', '#FF6B9D', '#34D399', '#60A5FA', '#FBBF24', '#F87171', '#A78BFA', '#FB923C']


class CommentSerializer(serializers.ModelSerializer):
    anon_label = serializers.SerializerMethodField()
    anon_color = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    is_post_author = serializers.SerializerMethodField()
    parent_label = serializers.SerializerMethodField()

    is_liked = serializers.SerializerMethodField()
    moderation_label = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'parent', 'content', 'like_count', 'created_at',
            'anon_label', 'anon_color', 'is_author', 'is_post_author', 'parent_label',
            'is_liked', 'status', 'moderation_reason', 'moderation_source', 'risk_level', 'review_deadline', 'moderation_label',
        ]

    def _get_user_map(self):
        if not hasattr(self, '_user_map_cache'):
            self._user_map_cache = self.context.get('user_map', {})
        return self._user_map_cache

    def get_anon_label(self, obj):
        user_map = self._get_user_map()
        idx = user_map.get(obj.author_id, 0)
        return ANON_LABELS[idx % len(ANON_LABELS)]

    def get_anon_color(self, obj):
        user_map = self._get_user_map()
        idx = user_map.get(obj.author_id, 0)
        return ANON_COLORS[idx % len(ANON_COLORS)]

    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False

    def get_is_post_author(self, obj):
        post_author_id = self.context.get('post_author_id')
        return obj.author_id == post_author_id

    def get_parent_label(self, obj):
        if obj.parent_id:
            user_map = self._get_user_map()
            idx = user_map.get(obj.parent.author_id, 0)
            post_author_id = self.context.get('post_author_id')
            if obj.parent.author_id == post_author_id:
                return '楼主'
            return ANON_LABELS[idx % len(ANON_LABELS)]
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.interactions.models import Like
            return Like.objects.filter(
                user=request.user, target_type='comment', target_id=obj.id
            ).exists()
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


class CreateCommentSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=200)
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError('评论内容不能为空')
        return value
