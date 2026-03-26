<template>
  <div
    class="post-card"
    :class="[`bubble-${post.bg_color}`, { 'short-bubble': isShortContent }]"
    :style="{ transform: `rotate(var(--card-rotation, 0deg))` }"
    @click="goDetail"
  >
    <!-- Header -->
    <div class="card-header">
      <div class="avatar-sm" :style="{ background: avatarColor }">
        {{ avatarText }}
      </div>
      <span class="nickname">{{ post.identity?.nickname || '匿名用户' }}</span>
      <span class="time">{{ timeAgo(post.created_at) }}</span>
    </div>

    <!-- Content: adaptive height based on length -->
    <p class="card-content" :class="{ clamp: contentText.length > 100 }">
      {{ contentText }}
    </p>

    <!-- Tag -->
    <div class="card-tag">
      <span class="tag-capsule">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>
    </div>

    <!-- Actions -->
    <div class="card-actions" @click.stop>
      <button class="action-btn" :class="{ active: post.is_liked }" @click="toggleLike">
        <span class="like-icon">{{ post.is_liked ? '♥' : '♡' }}</span>
        <span>{{ post.like_count }}</span>
      </button>
      <button class="action-btn" @click="goDetail">
        <span>💬</span>
        <span>{{ post.comment_count }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { postsApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{ post: any }>()
const emit = defineEmits(['liked'])
const router = useRouter()
const authStore = useAuthStore()

const contentText = computed(() => props.post.content_preview || props.post.content || '')
const isShortContent = computed(() => contentText.value.length < 50)

const avatarColor = computed(() => {
  const seed = props.post.identity?.avatar_seed || '777777'
  return `#${seed.substring(0, 6)}`
})

const avatarText = computed(() => {
  const nick = props.post.identity?.nickname || '?'
  return nick.charAt(2) || nick.charAt(0)
})

function tagEmoji(tag: string) {
  const map: Record<string, string> = {
    '表白': '💌', '吐槽': '😤', '求助': '🆘',
    '树洞': '🕳️', '失物招领': '🔍', '搭子': '🤝',
  }
  return map[tag] || ''
}

function timeAgo(dateStr: string) {
  const now = Date.now()
  const d = new Date(dateStr).getTime()
  const diff = Math.floor((now - d) / 1000)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`
  return new Date(dateStr).toLocaleDateString()
}

function goDetail() {
  router.push(`/post/${props.post.id}`)
}

async function toggleLike() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  try {
    const res = await postsApi.toggleLike(props.post.id)
    const data = res.data.data
    props.post.is_liked = data.is_liked
    props.post.like_count = data.like_count
    emit('liked')
  } catch { /* ignore */ }
}
</script>

<style scoped>
.post-card {
  border-radius: var(--card-radius);
  padding: var(--space-4);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: var(--shadow-sm);
  animation: bubble-in 0.3s ease-out both;
}

/* Short content → more rounded, smaller feel */
.post-card.short-bubble {
  border-radius: 28px;
  padding: var(--space-3) var(--space-4);
}

.post-card:nth-child(1) { animation-delay: 0ms; }
.post-card:nth-child(2) { animation-delay: 50ms; }
.post-card:nth-child(3) { animation-delay: 100ms; }
.post-card:nth-child(4) { animation-delay: 150ms; }
.post-card:nth-child(5) { animation-delay: 200ms; }
.post-card:nth-child(6) { animation-delay: 250ms; }

@keyframes bubble-in {
  from {
    opacity: 0;
    transform: translateY(20px) rotate(var(--card-rotation, 0deg));
  }
  to {
    opacity: 1;
    transform: translateY(0) rotate(var(--card-rotation, 0deg));
  }
}

/* Hover: bubble float up effect */
.post-card:hover {
  transform: translateY(-4px) scale(1.01) rotate(0deg) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.post-card:active {
  transform: scale(0.98) !important;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.avatar-sm {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.nickname {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.time {
  font-size: 12px;
  color: var(--text-secondary);
  margin-left: auto;
}

/* Content: natural height for short text, clamped for long text */
.card-content {
  font-size: 15px;
  line-height: 24px;
  color: var(--text-primary);
  margin-bottom: var(--space-3);
  word-break: break-word;
  white-space: pre-wrap;
}

.card-content.clamp {
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-tag {
  margin-bottom: var(--space-3);
}

.tag-capsule {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.06);
  color: var(--text-secondary);
}

.card-actions {
  display: flex;
  gap: var(--space-6);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 4px 0;
  transition: color 0.2s ease;
}

.action-btn:hover {
  color: var(--brand-primary);
  transform: none;
  box-shadow: none;
}

.action-btn.active {
  color: var(--brand-secondary);
}

.action-btn.active .like-icon {
  animation: like-bounce 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes like-bounce {
  0% { transform: scale(1); }
  30% { transform: scale(1.4); }
  60% { transform: scale(0.9); }
  100% { transform: scale(1); }
}

.action-btn span:first-child {
  font-size: 18px;
}
</style>
