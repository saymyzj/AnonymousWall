from rest_framework import serializers

from .models import Conversation, Notification, PrivateMessage


class PrivateMessageSerializer(serializers.ModelSerializer):
    mine = serializers.SerializerMethodField()

    class Meta:
        model = PrivateMessage
        fields = ['id', 'content', 'created_at', 'mine', 'is_read']

    def get_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.sender_id == request.user.id)


class ConversationSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    avatar_class = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    unread = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    post_ref = serializers.CharField(source='post.content', read_only=True)
    post_link = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'avatar', 'avatar_class', 'name', 'preview', 'unread', 'time',
            'post_ref', 'post_link', 'messages', 'is_blocked', 'owner_id',
        ]

    def _peer(self, obj):
        request = self.context.get('request')
        if request and request.user.id == obj.owner_id:
            return obj.participant
        return obj.owner

    def get_avatar(self, obj):
        peer = self._peer(obj)
        return peer.identities.order_by('-created_at').first().nickname[:1] if peer.identities.exists() else '匿'

    def get_avatar_class(self, obj):
        return f'a{(obj.id % 3) + 1}'

    def get_name(self, obj):
        peer = self._peer(obj)
        identity = peer.identities.order_by('-created_at').first()
        return identity.nickname if identity else f'匿名用户 #{peer.id}'

    def get_preview(self, obj):
        message = obj.messages.order_by('-created_at').first()
        return message.content if message else '还没有消息'

    def get_unread(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()

    def get_time(self, obj):
        message = obj.messages.order_by('-created_at').first()
        if not message:
            return ''
        return message.created_at.strftime('%m-%d %H:%M')

    def get_post_link(self, obj):
        return f'/post/{obj.post_id}'

    def get_messages(self, obj):
        messages = obj.messages.order_by('created_at')[:100]
        return PrivateMessageSerializer(messages, many=True, context=self.context).data


class NotificationSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'content', 'link', 'is_read', 'group', 'icon', 'time']

    def get_group(self, obj):
        today = obj.created_at.date()
        from django.utils import timezone
        now = timezone.localtime().date()
        if today == now:
            return '今天'
        if today == now.fromordinal(now.toordinal() - 1):
            return '昨天'
        return '更早'

    def get_icon(self, obj):
        return {
            'comment': '💬',
            'like': '❤️',
            'favorite': '⭐',
            'report': '⚠️',
            'system': '📣',
            'message': '✉️',
        }.get(obj.type, '🔔')

    def get_time(self, obj):
        return obj.created_at.strftime('%m-%d %H:%M')
