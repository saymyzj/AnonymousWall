<template>
  <div class="detail-page" v-if="post">
    <div class="detail-grid">
      <!-- Left: Post Bubble -->
      <div class="post-column">
        <div class="post-bubble" :class="`bubble-${post.bg_color}`">
          <div class="post-header">
            <div class="avatar" :style="{ background: avatarColor }">
              {{ avatarText }}
            </div>
            <div class="post-meta">
              <span class="nickname">{{ post.identity?.nickname || '匿名用户' }}</span>
              <span class="time">{{ timeAgo(post.created_at) }}</span>
            </div>
          </div>
          <p class="post-content">{{ post.content }}</p>
          <div class="post-tag">
            <span class="tag-capsule">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>
          </div>
          <div class="post-actions">
            <button class="action-btn" :class="{ active: post.is_liked }" @click="toggleLike">
              <span class="action-icon">{{ post.is_liked ? '♥' : '♡' }}</span>
              <span>{{ post.like_count }}</span>
            </button>
            <span class="action-btn">
              <span class="action-icon">💬</span>
              <span>{{ post.comment_count }}</span>
            </span>
            <button class="action-btn disabled">
              <span class="action-icon">↗</span>
              <span>分享</span>
            </button>
            <button v-if="post.is_author" class="action-btn delete" @click="deletePost">
              <span class="action-icon">🗑</span>
              <span>删除</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Comments -->
      <div class="comments-column">
        <div class="comments-panel">
          <h3 class="comments-title">评论 ({{ post.comment_count }})</h3>

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

          <!-- Inline Comment Input -->
          <div v-if="authStore.isLoggedIn && !authStore.isVerified" class="verify-hint">
            账号审核中，通过后即可评论
          </div>
          <div class="comment-input" v-if="authStore.isLoggedIn && authStore.isVerified">
            <div v-if="replyTo" class="reply-hint">
              回复 {{ replyTo.is_post_author ? '楼主' : replyTo.anon_label }}
              <button class="reply-cancel" @click="replyTo = null">×</button>
            </div>
            <div class="input-row" :class="{ expanded: inputExpanded }">
              <textarea
                ref="commentInputEl"
                v-model="commentText"
                placeholder="写评论..."
                maxlength="200"
                rows="1"
                @focus="inputExpanded = true"
                @blur="onInputBlur"
                @keydown.enter.exact.prevent="submitComment"
              ></textarea>
              <button class="send-btn" :disabled="!commentText.trim()" @click="submitComment">
                发送
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="loading-state">
    <van-loading type="spinner" color="var(--brand-primary)" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
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
  max-width: 1000px;
  margin: 0 auto;
}

.detail-grid {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 32px;
  align-items: start;
}

/* Post Bubble */
.post-bubble {
  border-radius: 24px;
  padding: 28px 32px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
}

.post-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
}

.post-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.nickname {
  font-size: 15px;
  font-weight: 600;
}

.time {
  font-size: 12px;
  color: var(--text-secondary);
}

.post-content {
  font-size: 16px;
  line-height: 28px;
  margin-bottom: 16px;
  word-break: break-word;
  white-space: pre-wrap;
}

.post-tag { margin-bottom: 16px; }
.tag-capsule {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.06);
  color: var(--text-secondary);
}

.post-actions {
  display: flex;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  padding: 6px 0;
  transition: color 0.2s ease;
}

.action-btn:hover { color: var(--brand-primary); transform: none; }
.action-btn.active { color: var(--brand-secondary); }
.action-btn.delete:hover { color: var(--color-error); }
.action-btn.disabled { cursor: default; opacity: 0.4; }
.action-icon { font-size: 18px; }

/* Comments Panel */
.comments-column {
  position: sticky;
  top: 88px;
  max-height: calc(100vh - 108px);
  overflow-y: auto;
}

.comments-panel {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.comments-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.no-comments {
  text-align: center;
  color: var(--text-placeholder);
  padding: 32px 0;
  font-size: 14px;
}

/* Comment Input */
.comment-input {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--divider);
}

.reply-hint {
  font-size: 12px;
  color: var(--brand-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.reply-cancel {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
  padding: 0;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 16px;
  padding: 8px 12px;
  border: 1.5px solid transparent;
  transition: all 0.2s ease;
}

.input-row:focus-within {
  border-color: var(--brand-primary);
  background: white;
  box-shadow: 0 0 0 3px rgba(124, 92, 252, 0.08);
}

.input-row textarea {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  resize: none;
  line-height: 20px;
  min-height: 20px;
  max-height: 100px;
  font-family: inherit;
  transition: min-height 0.2s ease;
}

.input-row.expanded textarea {
  min-height: 60px;
}

.input-row textarea::placeholder {
  color: var(--text-placeholder);
}

.send-btn {
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: none;
}

.send-btn:disabled {
  opacity: 0.4;
}

.verify-hint {
  margin-top: 16px;
  text-align: center;
  padding: 12px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}

.loading-state {
  text-align: center;
  padding: 64px 0;
}
</style>
