<template>
  <div class="comment-bubble">
    <div class="comment-header">
      <div class="anon-avatar" :style="{ background: comment.anon_color }">
        {{ comment.anon_label?.charAt(2) || 'A' }}
      </div>
      <span class="anon-label" :style="{ color: comment.anon_color }">
        {{ comment.is_post_author ? '楼主' : comment.anon_label }}
      </span>
      <span class="comment-time">{{ timeAgo(comment.created_at) }}</span>
    </div>

    <div class="comment-body">
      <span v-if="comment.parent_label" class="reply-to">
        回复 <b>{{ comment.parent_label }}</b>：
      </span>
      {{ comment.content }}
    </div>

    <div class="comment-actions">
      <button class="act-btn" :class="{ active: comment.is_liked }" @click="$emit('like', comment.id)">
        {{ comment.is_liked ? '♥' : '♡' }} {{ comment.like_count }}
      </button>
      <button class="act-btn" @click="$emit('reply', comment)">↩ 回复</button>
      <button v-if="comment.is_author" class="act-btn danger" @click="$emit('delete', comment.id)">删除</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ comment: any }>()
defineEmits(['reply', 'like', 'delete'])

function timeAgo(dateStr: string) {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return `${Math.floor(diff / 86400)}天前`
}
</script>

<style scoped>
.comment-bubble {
  padding: 12px 14px;
  margin-bottom: 8px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 14px;
  transition: background 0.2s ease;
}

.comment-bubble:hover {
  background: rgba(0, 0, 0, 0.05);
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.anon-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 11px;
  font-weight: 600;
}

.anon-label {
  font-size: 13px;
  font-weight: 600;
}

.comment-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-left: auto;
  opacity: 0.6;
}

.comment-body {
  font-size: 14px;
  line-height: 22px;
  color: var(--text-primary);
  word-break: break-word;
}

.reply-to {
  color: var(--text-secondary);
  font-size: 13px;
}

.comment-actions {
  display: flex;
  gap: 16px;
  margin-top: 6px;
}

.act-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 2px 0;
  opacity: 0.5;
  transition: all 0.2s ease;
}

.comment-bubble:hover .act-btn {
  opacity: 1;
}

.act-btn:hover {
  color: var(--brand-primary);
  transform: none;
}

.act-btn.active {
  color: var(--brand-secondary);
  opacity: 1;
}

.act-btn.danger:hover {
  color: var(--color-error);
}
</style>
