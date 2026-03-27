<template>
  <div class="comment-item">
    <div class="comment-header">
      <div class="anon-avatar" :style="{ background: comment.anon_color }">
        {{ comment.anon_label?.charAt(2) || 'A' }}
      </div>
      <div class="comment-meta">
        <div class="meta-top">
          <span class="anon-name">{{ comment.is_post_author ? '楼主' : comment.anon_label }}</span>
          <span v-if="comment.is_post_author" class="author-badge">楼主</span>
        </div>
        <span class="comment-time">{{ timeAgo(comment.created_at) }}</span>
      </div>
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
.comment-item {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.comment-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.anon-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.comment-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.meta-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.anon-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-1);
}

.author-badge {
  display: inline-block;
  padding: 1px 8px;
  border-radius: var(--radius-pill);
  background: var(--brand);
  color: white;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.6;
}

.comment-time {
  font-size: 12px;
  color: var(--text-3);
}

.comment-body {
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-1);
  word-break: break-word;
  white-space: pre-wrap;
  margin-left: 46px;
}

.reply-to {
  color: var(--brand);
  font-size: 14px;
  font-weight: 500;
}

.reply-to b {
  font-weight: 600;
}

.comment-actions {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  margin-left: 46px;
}

.act-btn {
  background: none;
  border: none;
  font-size: 13px;
  color: var(--text-3);
  cursor: pointer;
  padding: 2px 0;
  transition: all 0.2s ease;
}

.act-btn:hover {
  color: var(--brand);
}

.act-btn.active {
  color: var(--pink);
}

.act-btn.danger:hover {
  color: var(--color-error);
}
</style>
