<template>
  <div
    class="post-card"
    :class="[`bubble-${post.bg_color}`, { compact: isShortContent }]"
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

    <!-- Content -->
    <p class="card-content" :class="{ clamp: contentText.length > 100 }">
      {{ contentText }}
    </p>

    <!-- Footer: tag + stats -->
    <div class="card-footer">
      <span class="tag-capsule">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>
      <div class="card-stats" @click.stop>
        <button class="stat-btn" :class="{ liked: post.is_liked }" @click="toggleLike">
          <span class="stat-icon">{{ post.is_liked ? '♥' : '♡' }}</span>
          {{ post.like_count }}
        </button>
        <button class="stat-btn" @click="goDetail">
          <span class="stat-icon">💬</span>
          {{ post.comment_count }}
        </button>
      </div>
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
  border-radius: 20px;
  padding: 20px 24px;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s ease-out, box-shadow 0.3s ease-out;
  animation: bubble-appear 0.4s ease-out both;
  position: relative;
}

/* Short text → more compact and rounded */
.post-card.compact {
  padding: 16px 20px;
  border-radius: 24px;
}

/* Staggered appearance */
.post-card:nth-child(1) { animation-delay: 0ms; }
.post-card:nth-child(2) { animation-delay: 50ms; }
.post-card:nth-child(3) { animation-delay: 100ms; }
.post-card:nth-child(4) { animation-delay: 150ms; }
.post-card:nth-child(5) { animation-delay: 200ms; }
.post-card:nth-child(6) { animation-delay: 250ms; }
.post-card:nth-child(7) { animation-delay: 300ms; }
.post-card:nth-child(8) { animation-delay: 350ms; }

@keyframes bubble-appear {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Hover: float up with deeper shadow */
.post-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12);
}

.post-card:active {
  transform: translateY(-2px) scale(0.99);
}

/* Header */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.avatar-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 13px;
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
  opacity: 0.7;
}

/* Content */
.card-content {
  font-size: 15px;
  line-height: 24px;
  color: var(--text-primary);
  margin-bottom: 12px;
  word-break: break-word;
  white-space: pre-wrap;
}

.card-content.clamp {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Footer */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tag-capsule {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.06);
  color: var(--text-secondary);
}

.card-stats {
  display: flex;
  gap: 12px;
}

.stat-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 2px 0;
  opacity: 0.6;
  transition: all 0.2s ease;
}

.post-card:hover .stat-btn {
  opacity: 1;
}

.stat-btn:hover {
  color: var(--brand-primary);
  transform: none;
}

.stat-btn.liked {
  color: var(--brand-secondary);
  opacity: 1;
}

.stat-btn.liked .stat-icon {
  animation: like-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes like-pop {
  0% { transform: scale(1); }
  40% { transform: scale(1.4); }
  100% { transform: scale(1); }
}

.stat-icon {
  font-size: 16px;
}
</style>
