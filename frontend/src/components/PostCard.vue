<template>
  <div
    class="bubble"
    :class="[`bubble-${post.bg_color}`]"
    @click="goDetail"
  >
    <!-- Tag label -->
    <span class="tag-label">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>

    <!-- Content -->
    <p class="bubble-content" :class="{ clamp: contentText.length > 100 }">
      {{ contentText }}
    </p>

    <!-- Footer: avatar + name | stats -->
    <div class="bubble-footer">
      <div class="bubble-author">
        <div class="avatar-sm">{{ avatarText }}</div>
        <span class="author-name">{{ post.identity?.nickname || '匿名用户' }}</span>
      </div>
      <div class="bubble-stats" @click.stop>
        <button class="stat-btn" :class="{ liked: post.is_liked }" @click="toggleLike">
          <span>{{ post.is_liked ? '❤️' : '♡' }}</span>
          {{ post.like_count }}
        </button>
        <button class="stat-btn" @click="goDetail">
          <span>💬</span>
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
.bubble {
  border-radius: 24px;
  padding: 22px;
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  cursor: pointer;
  break-inside: avoid;
  margin-bottom: 20px;
  animation: bubble-appear 0.4s ease-out both;
}

.bubble:hover {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.15);
}

/* Staggered appearance */
.bubble:nth-child(1) { animation-delay: 0ms; }
.bubble:nth-child(2) { animation-delay: 50ms; }
.bubble:nth-child(3) { animation-delay: 100ms; }
.bubble:nth-child(4) { animation-delay: 150ms; }
.bubble:nth-child(5) { animation-delay: 200ms; }
.bubble:nth-child(6) { animation-delay: 250ms; }
.bubble:nth-child(7) { animation-delay: 300ms; }
.bubble:nth-child(8) { animation-delay: 350ms; }

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

/* Tag label */
.tag-label {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-2);
  margin-bottom: 12px;
}

/* Content */
.bubble-content {
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-1);
  margin-bottom: 16px;
  word-break: break-word;
  white-space: pre-wrap;
}

.bubble-content.clamp {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Footer */
.bubble-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.bubble-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar-sm {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--cyan));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.author-name {
  font-size: 13px;
  color: var(--text-2);
}

/* Stats */
.bubble-stats {
  display: flex;
  gap: 12px;
}

.stat-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--text-3);
  font-size: 12px;
  cursor: pointer;
  padding: 2px 0;
  opacity: 0.7;
  transition: all 0.2s ease;
}

.bubble:hover .stat-btn {
  opacity: 1;
}

.stat-btn:hover {
  color: var(--brand);
}

.stat-btn.liked {
  color: var(--pink);
  opacity: 1;
}

.stat-btn.liked span {
  animation: like-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes like-pop {
  0% { transform: scale(1); }
  40% { transform: scale(1.4); }
  100% { transform: scale(1); }
}
</style>
