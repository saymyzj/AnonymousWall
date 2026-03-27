<template>
  <article class="comment-item">
    <div class="comment-main">
      <div class="anon-avatar" :style="{ background: comment.anon_color }">
        {{ getIdentityInitial(comment.anon_label) }}
      </div>

      <div class="comment-body-wrap">
        <header class="comment-header">
          <div class="header-left">
            <span class="anon-name">{{ comment.is_post_author ? '楼主' : comment.anon_label }}</span>
            <span v-if="comment.is_post_author" class="author-badge">楼主</span>
            <span class="comment-time">{{ formatTimeAgo(comment.created_at) }}</span>
          </div>
        </header>

        <div class="comment-body">
          <span v-if="comment.parent_label" class="reply-to">
            @{{ comment.parent_label }}
          </span>
          {{ comment.content }}
        </div>

        <div class="comment-actions">
          <button class="act-btn" :class="{ active: comment.is_liked }" type="button" @click="$emit('like', comment.id)">
            {{ comment.is_liked ? '❤️' : '♡' }}
            <span>{{ comment.like_count }}</span>
          </button>
          <button class="act-btn" type="button" @click="$emit('reply', comment)">💬 回复</button>
          <button class="act-btn" type="button" @click="$emit('report', comment)">⚠️ 举报</button>
          <button v-if="comment.is_author" class="act-btn danger" type="button" @click="$emit('delete', comment.id)">
            删除
          </button>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { formatTimeAgo, getIdentityInitial } from '../utils/presentation'

defineProps<{ comment: any }>()
defineEmits(['reply', 'like', 'delete', 'report'])
</script>

<style scoped>
.comment-item {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.comment-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: 0;
}

.comment-main {
  display: flex;
  gap: 14px;
}

.anon-avatar {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #fff;
  font-size: 0.8125rem;
  font-weight: 700;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.comment-body-wrap {
  flex: 1;
  min-width: 0;
}

.comment-header {
  margin-bottom: 6px;
}

.header-left {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.anon-name {
  color: var(--text-1);
  font-size: 0.875rem;
  font-weight: 600;
}

.author-badge {
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  background: var(--brand);
  color: #fff;
  font-size: 0.6875rem;
  font-weight: 700;
}

.comment-time {
  color: var(--text-3);
  font-size: 0.75rem;
}

.comment-body {
  color: var(--text-1);
  font-size: 0.9375rem;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.reply-to {
  margin-right: 6px;
  color: var(--brand);
  font-weight: 500;
}

.comment-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  margin-top: 12px;
}

.act-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text-3);
  font-size: 0.8125rem;
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
