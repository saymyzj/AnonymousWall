from django.db.models import Q

from common.redis_client import RedisUnavailable, get_redis_client


def _notification_key(user_id: int) -> str:
    return f'user:{user_id}:notifications:unread'


def _message_key(user_id: int) -> str:
    return f'user:{user_id}:messages:unread'


def _cache_ttl() -> int:
    from django.conf import settings
    return int(getattr(settings, 'REDIS_UNREAD_TTL', 120))


def get_unread_summary(user) -> dict[str, int]:
    client = get_redis_client()
    notif_key = _notification_key(user.id)
    msg_key = _message_key(user.id)

    if client is not None:
        try:
            cached = client.mget([notif_key, msg_key])
            if cached and cached[0] is not None and cached[1] is not None:
                return {
                    'notifications': int(cached[0]),
                    'messages': int(cached[1]),
                }
        # Cache failures should never break the core product flow.
        except Exception:
            pass

    summary = recalculate_unread_summary(user)
    cache_unread_summary(user.id, summary['notifications'], summary['messages'])
    return summary


def recalculate_unread_summary(user) -> dict[str, int]:
    from apps.interactions.models import Conversation, Notification, PrivateMessage

    user_conversations = Conversation.objects.filter(Q(owner=user) | Q(participant=user))
    return {
        'notifications': Notification.objects.filter(user=user, is_read=False).count(),
        'messages': PrivateMessage.objects.filter(
            conversation__in=user_conversations,
            is_read=False,
        ).exclude(sender=user).count(),
    }


def cache_unread_summary(user_id: int, notifications: int, messages: int):
    client = get_redis_client()
    if client is None:
        return
    try:
        ttl = _cache_ttl()
        client.set(_notification_key(user_id), int(notifications), ex=ttl)
        client.set(_message_key(user_id), int(messages), ex=ttl)
    except Exception:
        return


def set_notification_unread_count(user_id: int, count: int):
    client = get_redis_client()
    if client is None:
        return
    try:
        client.set(_notification_key(user_id), int(count), ex=_cache_ttl())
    except Exception:
        return


def set_message_unread_count(user_id: int, count: int):
    client = get_redis_client()
    if client is None:
        return
    try:
        client.set(_message_key(user_id), int(count), ex=_cache_ttl())
    except Exception:
        return


def invalidate_notification_unread(user_id: int):
    client = get_redis_client()
    if client is None:
        return
    try:
        client.delete(_notification_key(user_id))
    except Exception:
        return


def invalidate_message_unread(user_id: int):
    client = get_redis_client()
    if client is None:
        return
    try:
        client.delete(_message_key(user_id))
    except Exception:
        return
