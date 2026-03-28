<template>
  <article
    class="bubble bubble-surface"
    :class="bubbleClass"
    @click="goDetail()"
  >
    <div class="bubble-top">
      <span class="tag-label">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>
      <span class="bubble-time">{{ formatTimeAgo(post.created_at) }}</span>
    </div>

    <p class="bubble-content" :class="{ clamp: contentText.length > 100 }">
      <template v-for="(segment, index) in highlightedContent" :key="`${segment.text}-${index}`">
        <mark v-if="segment.highlight">{{ segment.text }}</mark>
        <template v-else>{{ segment.text }}</template>
      </template>
    </p>

    <div v-if="post.images?.length" class="bubble-images">
      <img
        v-for="image in post.images.slice(0, 3)"
        :key="image.id"
        :src="image.thumbnail_url || image.image_url"
        alt=""
      />
    </div>

    <footer class="bubble-footer" @click.stop>
      <div class="bubble-author">
        <div class="avatar-sm">{{ avatarText }}</div>
        <div class="author-meta">
          <span class="author-name">{{ post.identity?.nickname || '匿名用户' }}</span>
          <span class="author-sub">一颗缓慢漂浮的匿名气泡</span>
        </div>
      </div>

      <div class="bubble-stats">
        <button class="stat-btn" :class="{ liked: post.is_liked }" type="button" @click="toggleLike">
          <span>{{ post.is_liked ? '❤️' : '♡' }}</span>
          <span>{{ post.like_count }}</span>
        </button>
        <button class="stat-btn" type="button" @click="goDetail('#comments')">
          <span>💬</span>
          <span>{{ post.comment_count }}</span>
        </button>
        <span class="stat-meta">⭐ {{ post.favorite_count }}</span>
      </div>
    </footer>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { postsApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'
import { formatTimeAgo, getIdentityInitial, tagEmoji } from '../utils/presentation'

const props = defineProps<{ post: any; searchTerm?: string }>()
const emit = defineEmits(['liked'])

const router = useRouter()
const authStore = useAuthStore()

const contentText = computed(() => props.post.content_preview || props.post.content || '')
const avatarText = computed(() => getIdentityInitial(props.post.identity?.nickname))
const bubbleClass = computed(() => `bubble-${props.post.bg_color || 7}`)
const highlightedContent = computed(() => {
  const keyword = props.searchTerm?.trim()
  if (!keyword) return [{ text: contentText.value, highlight: false }]

  const lower = contentText.value.toLowerCase()
  const matcher = keyword.toLowerCase()
  const segments: Array<{ text: string; highlight: boolean }> = []
  let cursor = 0

  while (cursor < contentText.value.length) {
    const hit = lower.indexOf(matcher, cursor)
    if (hit === -1) {
      segments.push({ text: contentText.value.slice(cursor), highlight: false })
      break
    }
    if (hit > cursor) {
      segments.push({ text: contentText.value.slice(cursor, hit), highlight: false })
    }
    segments.push({ text: contentText.value.slice(hit, hit + keyword.length), highlight: true })
    cursor = hit + keyword.length
  }

  return segments
})

function goDetail(hash = '') {
  router.push({
    path: `/post/${props.post.id}`,
    hash,
  })
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
  } catch {
    // keep card interaction quiet for now
  }
}
</script>

<style scoped>
.bubble {
  break-inside: avoid;
  margin-bottom: 20px;
  padding: 22px;
  border-radius: var(--radius-bubble);
  cursor: pointer;
  transition:
    transform 0.3s ease,
    border-color 0.3s ease,
    box-shadow 0.3s ease;
}

.bubble:hover {
  transform: translateY(-4px);
  border-color: var(--border-hover);
  box-shadow: 0 18px 46px var(--bubble-glow, var(--glow-white));
}

.bubble-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.tag-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: fit-content;
  padding: 5px 12px;
  border-radius: var(--radius-pill);
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-2);
  font-size: 0.75rem;
  font-weight: 600;
}

.bubble-time {
  font-size: 0.75rem;
  color: var(--text-3);
}

.bubble-content {
  margin: 0 0 18px;
  color: var(--text-1);
  font-size: 0.9375rem;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble-content mark {
  padding: 0 2px;
  border-radius: 6px;
  background: rgba(124, 92, 252, 0.22);
  color: inherit;
}

.bubble-content.clamp {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}

.bubble-images {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 16px;
}

.bubble-images img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: var(--radius-img);
  border: 1px solid var(--border);
}

.bubble-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.bubble-author {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.avatar-sm {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--gradient-avatar);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
}

.author-meta {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.author-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-1);
  font-size: 0.8125rem;
  font-weight: 600;
}

.author-sub {
  color: var(--text-3);
  font-size: 0.75rem;
}

.bubble-stats {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.stat-btn,
.stat-meta {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-3);
  font-size: 0.75rem;
}

.stat-btn {
  border: 0;
  padding: 0;
  background: transparent;
}

.stat-btn:hover {
  color: var(--brand);
}

.stat-btn.liked {
  color: var(--pink);
}

@media (max-width: 599px) {
  .bubble-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .bubble-stats {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
