<template>
  <div class="detail-page" v-if="post">
    <!-- Post Bubble (large, centered) -->
    <div class="post-bubble" :class="`bubble-${post.bg_color}`">
      <span class="tag-label">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>
      <p class="post-content">{{ post.content }}</p>
      <!-- Author area with divider -->
      <div class="post-divider"></div>
      <div class="post-author">
        <div class="author-avatar">{{ avatarText }}</div>
        <div class="author-info">
          <span class="author-name">{{ post.identity?.nickname || '匿名用户' }}</span>
          <span class="author-time">{{ timeAgo(post.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Action Bar -->
    <div class="action-bar">
      <button class="action-pill" :class="{ active: post.is_liked }" @click="toggleLike">
        {{ post.is_liked ? '❤️' : '♡' }} {{ post.like_count }}
      </button>
      <button class="action-pill">⭐ 收藏</button>
      <button class="action-pill">🔗 分享</button>
      <button v-if="post.is_author" class="action-pill danger" @click="deletePost">🗑 删除</button>
    </div>

    <!-- Comments Section -->
    <div class="comments-section">
      <h3 class="comments-title">评论 <span class="comments-count">{{ post.comment_count }}</span></h3>

      <!-- Comment Input (top) -->
      <div class="comment-input-card" v-if="authStore.isLoggedIn && authStore.isVerified">
        <div class="input-header">
          <div class="input-avatar">🌟</div>
          <span class="input-hint">以匿名身份评论</span>
        </div>
        <div v-if="replyTo" class="reply-hint">
          回复 {{ replyTo.is_post_author ? '楼主' : replyTo.anon_label }}
          <button @click="replyTo = null">×</button>
        </div>
        <textarea
          ref="commentInputEl"
          v-model="commentText"
          placeholder="写下你的评论..."
          maxlength="200"
          @keydown.enter.exact.prevent="submitComment"
        ></textarea>
        <div class="input-toolbar">
          <span class="char-count">{{ commentText.length }} / 200</span>
          <button class="submit-btn" :disabled="!commentText.trim()" @click="submitComment">发布</button>
        </div>
      </div>

      <!-- Comment List -->
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
      <div v-else class="empty-comments">还没有评论，来说两句吧</div>
    </div>
  </div>
  <div v-else class="loading-state">加载中...</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsApi } from '../api/posts'
import { commentsApi } from '../api/comments'
import { useAuthStore } from '../stores/auth'
import CommentTree from '../components/CommentTree.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const post = ref<any>(null)
const flatComments = ref<any[]>([])
const commentText = ref('')
const replyTo = ref<any>(null)
const inputExpanded = ref(false)
const commentInputEl = ref<HTMLTextAreaElement>()

function onInputBlur() {
  if (!commentText.value.trim()) inputExpanded.value = false
}

const commentTree = computed(() => {
  const list = flatComments.value
  if (!list.length) return []
  const map = new Map<number, any>()
  const roots: any[] = []
  for (const c of list) map.set(c.id, { ...c, children: [] })
  for (const c of list) {
    const node = map.get(c.id)!
    if (c.parent) {
      const parentNode = map.get(c.parent)
      if (parentNode) parentNode.children.push(node)
      else roots.push(node)
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
    alert('帖子不存在')
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
  inputExpanded.value = true
  nextTick(() => commentInputEl.value?.focus())
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
    alert(e.response?.data?.message || '评论失败')
  }
}

async function deletePost() {
  try {
    await postsApi.delete(postId)
    alert('删除成功')
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
  max-width: 720px;
  margin: 0 auto;
  padding: 0 20px 100px;
}

/* Post Bubble */
.post-bubble {
  border-radius: 28px;
  padding: 40px 36px;
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
  position: relative;
}

.post-bubble::after {
  content: '';
  position: absolute;
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.08);
}

.tag-label {
  display: inline-block;
  padding: 4px 14px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-2);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.post-content {
  font-size: 20px;
  line-height: 1.9;
  letter-spacing: 0.3px;
  color: var(--text-1);
  margin: 16px 0;
  word-break: break-word;
  white-space: pre-wrap;
}

.post-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 20px 0;
}

.post-author {
  display: flex;
  gap: 12px;
  align-items: center;
}

.author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--pink));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  font-weight: 600;
  flex-shrink: 0;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-1);
}

.author-time {
  font-size: 13px;
  color: var(--text-2);
}

/* Action Bar */
.action-bar {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 28px;
}

.action-pill {
  padding: 8px 18px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-2);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-pill:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-1);
}

.action-pill.active {
  color: var(--pink);
  border-color: rgba(255, 107, 157, 0.3);
  background: rgba(255, 107, 157, 0.08);
}

.action-pill.danger:hover {
  color: var(--color-error);
}

/* Comments Section */
.comments-section {
  margin-top: 40px;
}

.comments-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-1);
}

.comments-count {
  font-size: 14px;
  color: var(--text-3);
  font-weight: 400;
}

/* Comment Input Card */
.comment-input-card {
  margin-top: 20px;
  padding: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.2s ease;
}

.comment-input-card:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(124, 92, 252, 0.25);
}

.input-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}

.input-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--cyan));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.input-hint {
  font-size: 13px;
  color: var(--text-3);
}

.reply-hint {
  font-size: 13px;
  color: var(--brand);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.reply-hint button {
  background: none;
  border: none;
  color: var(--text-2);
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  line-height: 1;
}

.comment-input-card textarea {
  width: 100%;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  color: var(--text-1);
  font-size: 15px;
  line-height: 1.6;
  resize: none;
  outline: none;
  min-height: 48px;
  max-height: 160px;
  font-family: inherit;
  padding-bottom: 12px;
  box-sizing: border-box;
}

.comment-input-card textarea::placeholder {
  color: var(--text-3);
}

.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.char-count {
  font-size: 12px;
  color: var(--text-3);
}

.submit-btn {
  padding: 6px 20px;
  border-radius: 999px;
  background: var(--brand);
  color: white;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  filter: brightness(1.15);
}

.submit-btn:disabled {
  opacity: 0.4;
  cursor: default;
}

/* Comment List */
.comment-list {
  margin-top: 24px;
}

.empty-comments {
  text-align: center;
  padding: 40px 0;
  color: var(--text-3);
  font-size: 14px;
}

.loading-state {
  text-align: center;
  padding: 64px;
  color: var(--text-2);
}

/* Responsive */
@media (max-width: 768px) {
  .detail-page {
    padding: 0 16px 80px;
  }

  .post-bubble {
    padding: 28px 24px;
  }

  .post-content {
    font-size: 17px;
  }
}
</style>
