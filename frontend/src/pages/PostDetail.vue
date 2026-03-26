<template>
  <div class="detail-page" v-if="post">
    <!-- Post Content -->
    <div class="post-bubble" :class="`bubble-${post.bg_color}`">
      <div class="post-header">
        <div class="avatar-sm" :style="{ background: avatarColor }">
          {{ avatarText }}
        </div>
        <span class="nickname">{{ post.identity?.nickname || '匿名用户' }}</span>
        <span class="time">{{ timeAgo(post.created_at) }}</span>
      </div>
      <p class="post-content">{{ post.content }}</p>
      <div class="post-tag">
        <span class="tag-capsule">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>
      </div>
      <div class="post-actions">
        <button class="action-btn" :class="{ active: post.is_liked }" @click="toggleLike">
          {{ post.is_liked ? '♥' : '♡' }} {{ post.like_count }}
        </button>
        <span class="action-btn">💬 {{ post.comment_count }}</span>
        <button v-if="post.is_author" class="action-btn delete" @click="deletePost">🗑 删除</button>
      </div>
    </div>

    <!-- Comments -->
    <div class="comments-section">
      <h3>评论 ({{ post.comment_count }})</h3>
      <div v-if="commentTree.length > 0" class="comment-list">
        <CommentTree
          v-for="c in commentTree"
          :key="c.id"
          :comment="c"
          :depth="0"
          @reply="startReply"
          @like="toggleCommentLike"
          @delete="deleteComment"
        />
      </div>
      <div v-else class="no-comments">还没有评论，来说两句吧</div>
    </div>

    <!-- Comment Input -->
    <div v-if="authStore.isLoggedIn && !authStore.isVerified" class="verify-hint safe-bottom">
      账号审核中，通过后即可评论
    </div>
    <div class="comment-input-bar safe-bottom" v-if="authStore.isLoggedIn && authStore.isVerified">
      <div v-if="replyTo" class="reply-hint">
        回复 {{ replyTo.is_post_author ? '楼主' : replyTo.anon_label }}
        <button @click="replyTo = null">×</button>
      </div>
      <div class="input-row">
        <input
          v-model="commentText"
          placeholder="写评论..."
          maxlength="200"
          @keyup.enter="submitComment"
        />
        <button class="send-btn" :disabled="!commentText.trim()" @click="submitComment">发送</button>
      </div>
    </div>
  </div>
  <div v-else class="loading">
    <van-loading type="spinner" color="var(--brand-primary)" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsApi } from '../api/posts'
import { commentsApi } from '../api/comments'
import { useAuthStore } from '../stores/auth'
import CommentTree from '../components/CommentTree.vue'
import { showToast } from 'vant'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const post = ref<any>(null)
const flatComments = ref<any[]>([])
const commentText = ref('')
const replyTo = ref<any>(null)

// Build comment tree from flat list
const commentTree = computed(() => {
  const list = flatComments.value
  if (!list.length) return []

  const map = new Map<number, any>()
  const roots: any[] = []

  for (const c of list) {
    map.set(c.id, { ...c, children: [] })
  }

  for (const c of list) {
    const node = map.get(c.id)!
    if (c.parent) {
      const parentNode = map.get(c.parent)
      if (parentNode) {
        parentNode.children.push(node)
      } else {
        roots.push(node)
      }
    } else {
      roots.push(node)
    }
  }

  return roots
})

const postId = Number(route.params.id)

const avatarColor = ref('#777')
const avatarText = ref('?')

function tagEmoji(tag: string) {
  const map: Record<string, string> = {
    '表白': '💌', '吐槽': '😤', '求助': '🆘',
    '树洞': '🕳️', '失物招领': '🔍', '搭子': '🤝',
  }
  return map[tag] || ''
}

function timeAgo(dateStr: string) {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return `${Math.floor(diff / 86400)}天前`
}

async function loadPost() {
  try {
    const res = await postsApi.getDetail(postId)
    post.value = res.data.data
    const seed = post.value.identity?.avatar_seed || '777777'
    avatarColor.value = `#${seed.substring(0, 6)}`
    const nick = post.value.identity?.nickname || '?'
    avatarText.value = nick.charAt(2) || nick.charAt(0)
  } catch {
    showToast('帖子不存在')
    router.push('/')
  }
}

async function loadComments() {
  try {
    const res = await commentsApi.getList(postId)
    flatComments.value = res.data.results || []
  } catch { /* ignore */ }
}

async function toggleLike() {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  try {
    const res = await postsApi.toggleLike(postId)
    post.value.is_liked = res.data.data.is_liked
    post.value.like_count = res.data.data.like_count
  } catch { /* ignore */ }
}

async function toggleCommentLike(commentId: number) {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  try {
    const res = await commentsApi.toggleLike(commentId)
    const c = flatComments.value.find((x: any) => x.id === commentId)
    if (c) {
      c.is_liked = res.data.data.is_liked
      c.like_count = res.data.data.like_count
    }
  } catch { /* ignore */ }
}

function startReply(comment: any) {
  replyTo.value = comment
}

async function submitComment() {
  if (!commentText.value.trim()) return
  try {
    await commentsApi.create(postId, {
      content: commentText.value,
      parent_id: replyTo.value?.id || null,
    })
    commentText.value = ''
    replyTo.value = null
    await loadComments()
    if (post.value) post.value.comment_count++
  } catch (e: any) {
    showToast(e.response?.data?.message || '评论失败')
  }
}

async function deletePost() {
  try {
    await postsApi.delete(postId)
    showToast('删除成功')
    router.push('/')
  } catch { /* ignore */ }
}

async function deleteComment(commentId: number) {
  try {
    await commentsApi.delete(commentId)
    await loadComments()
    if (post.value) post.value.comment_count--
  } catch { /* ignore */ }
}

onMounted(() => {
  loadPost()
  loadComments()
})
</script>

<style scoped>
.detail-page {
  max-width: 600px;
  margin: 0 auto;
  padding-bottom: 80px;
}

.post-bubble {
  border-radius: var(--card-radius);
  padding: var(--space-4);
  margin-bottom: var(--space-5);
}

.post-header {
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
}

.nickname { font-size: 13px; font-weight: 600; }
.time { font-size: 12px; color: var(--text-secondary); margin-left: auto; }

.post-content {
  font-size: 15px;
  line-height: 24px;
  margin-bottom: var(--space-3);
  word-break: break-word;
  white-space: pre-wrap;
}

.post-tag { margin-bottom: var(--space-3); }
.tag-capsule {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.06);
}

.post-actions {
  display: flex;
  gap: var(--space-6);
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
}
.action-btn.active { color: var(--brand-secondary); }
.action-btn.delete { color: var(--color-error); }

.comments-section {
  background: var(--card-bg);
  border-radius: 20px;
  padding: var(--space-4);
}

.comments-section h3 {
  font-size: 16px;
  margin-bottom: var(--space-3);
}

.no-comments {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--space-6) 0;
  font-size: 14px;
}

.comment-input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-top: 1px solid var(--divider);
  padding: var(--space-3) var(--space-4);
  z-index: 100;
}

.reply-hint {
  font-size: 12px;
  color: var(--brand-primary);
  margin-bottom: var(--space-2);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.reply-hint button {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
}

.input-row {
  display: flex;
  gap: var(--space-2);
}

.input-row input {
  flex: 1;
  height: 40px;
  border: 1px solid var(--divider);
  border-radius: 20px;
  padding: 0 var(--space-4);
  font-size: 14px;
  background: transparent;
  color: var(--text-primary);
  outline: none;
}

.input-row input:focus {
  border-color: var(--brand-primary);
}

.send-btn {
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 0 16px;
  font-size: 14px;
  cursor: pointer;
}

.send-btn:disabled {
  opacity: 0.5;
}

.verify-hint {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  padding: var(--space-3) var(--space-4);
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-top: 1px solid var(--divider);
  font-size: 13px;
  color: var(--text-secondary);
  z-index: 100;
}

.loading {
  text-align: center;
  padding: var(--space-10) 0;
}
</style>
