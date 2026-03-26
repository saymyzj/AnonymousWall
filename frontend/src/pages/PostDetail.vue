<template>
  <div class="detail-page" v-if="post">
    <div class="detail-grid">
      <!-- Left: Post Content -->
      <div class="post-column">
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
      </div>

      <!-- Right: Comments -->
      <div class="comments-column">
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

          <!-- Inline Comment Input -->
          <div v-if="authStore.isLoggedIn && !authStore.isVerified" class="verify-hint">
            账号审核中，通过后即可评论
          </div>
          <div class="comment-input-card" v-if="authStore.isLoggedIn && authStore.isVerified">
            <div v-if="replyTo" class="reply-hint">
              回复 {{ replyTo.is_post_author ? '楼主' : replyTo.anon_label }}
              <button @click="replyTo = null">×</button>
            </div>
            <div class="input-row">
              <textarea
                ref="commentInput"
                v-model="commentText"
                placeholder="写评论..."
                maxlength="200"
                rows="1"
                class="comment-textarea"
                @focus="inputExpanded = true"
                @blur="onInputBlur"
                @keydown.enter.exact.prevent="submitComment"
              ></textarea>
              <button class="send-btn" :disabled="!commentText.trim()" @click="submitComment">发送</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="loading">
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
const commentInput = ref<HTMLTextAreaElement>()

function onInputBlur() {
  if (!commentText.value.trim()) {
    inputExpanded.value = false
  }
}

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
  inputExpanded.value = true
  nextTick(() => commentInput.value?.focus())
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

/* Desktop: dual-column grid */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-5);
}

@media (min-width: 768px) {
  .detail-grid {
    grid-template-columns: 3fr 2fr;
    gap: var(--space-8);
    align-items: start;
  }

  .comments-column {
    position: sticky;
    top: 80px;
    max-height: calc(100vh - 100px);
    overflow-y: auto;
  }
}

.post-bubble {
  border-radius: var(--card-radius);
  padding: var(--space-5);
}

.post-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.avatar-sm {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 15px;
  font-weight: 600;
}

.nickname { font-size: 14px; font-weight: 600; }
.time { font-size: 12px; color: var(--text-secondary); margin-left: auto; }

.post-content {
  font-size: 16px;
  line-height: 26px;
  margin-bottom: var(--space-4);
  word-break: break-word;
  white-space: pre-wrap;
}

.post-tag { margin-bottom: var(--space-3); }
.tag-capsule {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
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
  transition: color 0.2s ease;
}
.action-btn:hover { color: var(--brand-primary); transform: none; box-shadow: none; }
.action-btn.active { color: var(--brand-secondary); }
.action-btn.delete { color: var(--color-error); }

/* Comments Section */
.comments-section {
  background: var(--card-bg);
  border-radius: 20px;
  padding: var(--space-5);
}

.comments-section h3 {
  font-size: 16px;
  margin-bottom: var(--space-4);
  font-weight: 600;
}

.no-comments {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--space-6) 0;
  font-size: 14px;
}

/* Inline Comment Input — inside comments section, not fixed bottom */
.comment-input-card {
  margin-top: var(--space-4);
  padding: var(--space-3);
  background: rgba(0, 0, 0, 0.03);
  border-radius: 16px;
  border: 1px solid var(--divider);
  transition: border-color 0.2s ease;
}

.comment-input-card:focus-within {
  border-color: var(--brand-primary);
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
  align-items: flex-end;
}

.comment-textarea {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  resize: none;
  line-height: 20px;
  min-height: 20px;
  max-height: 120px;
  font-family: inherit;
}

.comment-textarea::placeholder {
  color: var(--text-placeholder);
}

.send-btn {
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: 16px;
  padding: 6px 16px;
  font-size: 13px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  filter: brightness(1.1);
}

.send-btn:disabled {
  opacity: 0.5;
}

.verify-hint {
  margin-top: var(--space-4);
  text-align: center;
  padding: var(--space-3);
  background: rgba(0, 0, 0, 0.03);
  border-radius: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}

.loading {
  text-align: center;
  padding: var(--space-10) 0;
}
</style>
