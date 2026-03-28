<template>
  <div v-if="post" class="detail-page">
    <!-- Post Card -->
    <article class="post-card">
      <div class="post-accent" :class="bubbleClass"></div>
      <div class="post-inner">
        <div class="post-top">
          <span class="tag-label">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>
          <span v-if="post.auto_destroy_at" class="destroy-hint">24h 后自毁</span>
        </div>

        <p class="post-content">{{ post.content }}</p>

        <div v-if="post.images?.length" class="post-images">
          <img v-for="image in post.images" :key="image.id" :src="image.image_url" alt="" />
        </div>

        <div v-if="post.poll" class="poll-card">
          <div class="poll-title">{{ post.poll.question || '这个投票，你会怎么选？' }}</div>
          <div class="poll-options">
            <button
              v-for="option in post.poll.options"
              :key="option.id"
              class="poll-option"
              :class="{ selected: post.poll.selected_option_id === option.id }"
              type="button"
              :disabled="post.poll.has_voted"
              @click="votePoll(option.id)"
            >
              <span>{{ option.text }}</span>
              <strong v-if="post.poll.has_voted">{{ option.percentage }}%</strong>
            </button>
          </div>
        </div>

        <div class="post-footer">
          <div class="author-avatar">{{ avatarText }}</div>
          <div class="author-info">
            <span class="author-name">{{ post.identity?.nickname || '匿名用户' }}</span>
            <span class="author-time">{{ formatTimeAgo(post.created_at) }}</span>
          </div>
          <span class="post-meta">
            {{ post.comment_count }} 评论 · {{ post.favorite_count }} 收藏
          </span>
        </div>
      </div>
    </article>

    <!-- Action Bar -->
    <div class="action-bar">
      <button class="action-pill" :class="{ active: post.is_liked }" type="button" @click="toggleLike">
        <span class="action-icon" :class="{ 'animate-bounce-in': likeAnimating }">{{ post.is_liked ? '❤️' : '♡' }}</span>
        {{ post.like_count }}
      </button>
      <button class="action-pill" :class="{ active: post.is_favorited }" type="button" @click="toggleFavorite">
        <span class="action-icon" :class="{ 'animate-bounce-in': favAnimating }">⭐</span>
        {{ post.favorite_count }}
      </button>
      <button class="action-pill" type="button" @click="showShareCard = true">
        🔗 分享
      </button>
      <button class="action-pill dm" type="button" :disabled="!canDirectMessage" @click="openMessageComposer">
        ✉️ 私信
      </button>
      <button class="action-pill" type="button" @click="reportPanelOpen = !reportPanelOpen">
        ⚠️ 举报
      </button>
      <button v-if="post.is_author" class="action-pill danger" type="button" @click="deletePost">
        🗑 删除
      </button>
      <button v-if="post.is_author" class="action-pill" type="button" @click="startEdit">
        ✏️ 编辑
      </button>
    </div>

    <!-- Report Panel -->
    <GlassCard v-if="reportPanelOpen" class="floating-panel">
      <div class="panel-head">
        <strong>举报{{ reportTarget.label }}</strong>
        <button type="button" @click="reportPanelOpen = false">关闭</button>
      </div>
      <div class="reason-chips">
        <button
          v-for="reason in reportReasons"
          :key="reason"
          class="ghost-pill"
          :class="{ active: reportReason === reason }"
          type="button"
          @click="reportReason = reason"
        >
          {{ reason }}
        </button>
      </div>
      <textarea v-model="reportDetail" maxlength="100" placeholder="补充说明（可选，100字内）"></textarea>
      <div class="panel-foot">
        <span>{{ reportDetail.length }} / 100</span>
        <button class="pill-button brand" type="button" :disabled="!reportReason" @click="submitReport">提交举报</button>
      </div>
    </GlassCard>

    <!-- Edit Panel -->
    <GlassCard v-if="editPanelOpen" class="floating-panel">
      <div class="panel-head">
        <strong>编辑帖子</strong>
        <button type="button" @click="editPanelOpen = false">关闭</button>
      </div>
      <textarea v-model="editContent" maxlength="500" placeholder="修改帖子内容"></textarea>
      <label class="edit-toggle">
        <input v-model="editAllowMessages" type="checkbox" />
        <span>允许匿名私信</span>
      </label>
      <div class="panel-foot">
        <span>{{ editContent.length }} / 500</span>
        <button class="pill-button brand" type="button" :disabled="!editContent.trim()" @click="submitEdit">保存修改</button>
      </div>
    </GlassCard>

    <!-- Message Panel -->
    <GlassCard v-if="messagePanelOpen" class="floating-panel">
      <div class="panel-head">
        <div>
          <strong>发送匿名私信</strong>
          <p class="panel-subtitle">消息会进入私信中心，楼主回复后你也能继续在会话里交流。</p>
        </div>
        <button type="button" @click="closeMessageComposer">关闭</button>
      </div>
      <div class="message-tags">
        <span>发送对象：{{ post.identity?.nickname || '匿名楼主' }}</span>
        <span>关联帖子：{{ post.tag }}</span>
      </div>
      <textarea
        v-model="messageDraft"
        maxlength="300"
        placeholder="写下你想悄悄说的话，支持 300 字以内。"
      ></textarea>
      <div class="panel-foot">
        <span>{{ messageDraft.length }} / 300</span>
        <button
          class="pill-button brand"
          type="button"
          :disabled="!messageDraft.trim() || messageSending"
          @click="submitDirectMessage"
        >
          {{ messageSending ? '发送中...' : '发送私信' }}
        </button>
      </div>
    </GlassCard>

    <!-- Comments Section -->
    <section id="comments" ref="commentsSectionRef" class="comments-section">
      <div class="comments-title">
        <h3>评论</h3>
        <span class="comments-count">{{ post.comment_count }} 条</span>
      </div>

      <!-- Comment Input -->
      <CommentComposer
        v-if="authStore.isLoggedIn && authStore.isVerified && !replyTo"
        v-model="commentText"
        :avatar-text="myAvatarText"
        :submitting="commentSubmitting"
        @submit="submitComment"
      />

      <div v-else-if="!authStore.isLoggedIn || !authStore.isVerified" class="login-hint">
        登录并完成认证后，就可以在这里留下你的匿名回应。
      </div>

      <!-- Comment List -->
      <div v-if="commentTree.length" class="comment-list stagger-fade-in">
        <CommentTree
          v-for="comment in commentTree"
          :key="comment.id"
          :comment="comment"
          :depth="0"
          :reply-target-id="authStore.isLoggedIn && authStore.isVerified ? (replyTo?.id || null) : null"
          :comment-text="commentText"
          :comment-submitting="commentSubmitting"
          :my-avatar-text="myAvatarText"
          :reply-label="replyTargetName"
          @reply="startReply"
          @like="toggleCommentLike"
          @delete="deleteComment"
          @report="startReportComment"
          @update:comment-text="commentText = $event"
          @cancel-reply="cancelReply"
          @blur-exit-reply="cancelReply"
          @submit-reply="submitComment"
        />
      </div>

      <div v-else class="empty-comments">
        <div class="empty-icon">💭</div>
        <p>第一条评论，会成为这颗气泡的第一束回声。</p>
      </div>
    </section>
  </div>

  <div v-else class="loading-wrap">
    <div class="loading-card">
      <div class="spinner"></div>
      <h3>正在接入这颗气泡</h3>
      <p>{{ loadingMessage }}</p>
    </div>
  </div>

  <ShareCardModal v-if="showShareCard && post" :post="post" @close="showShareCard = false" />
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommentComposer from '../components/CommentComposer.vue'
import CommentTree from '../components/CommentTree.vue'
import GlassCard from '../components/GlassCard.vue'
import ShareCardModal from '../components/ShareCardModal.vue'
import { commentsApi } from '../api/comments'
import { messagesApi } from '../api/messages'
import { postsApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'
import { formatTimeAgo, getIdentityInitial, tagEmoji } from '../utils/presentation'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const post = ref<any>(null)
const flatComments = ref<any[]>([])
const commentText = ref('')
const commentSubmitting = ref(false)
const replyTo = ref<any>(null)
const reportPanelOpen = ref(false)
const editPanelOpen = ref(false)
const messagePanelOpen = ref(false)
const reportReason = ref('')
const reportDetail = ref('')
const showShareCard = ref(false)
const editContent = ref('')
const editAllowMessages = ref(true)
const messageDraft = ref('')
const messageSending = ref(false)
const loadingMessage = ref('详情页内容加载中，请稍候。')
const commentsSectionRef = ref<HTMLElement>()
const likeAnimating = ref(false)
const favAnimating = ref(false)
const reportReasons = ['广告引流', '人身攻击', '色情低俗', '隐私泄露', '其他']

const postId = computed(() => Number(route.params.id))
const bubbleClass = computed(() => `accent-${post.value?.bg_color || 7}`)
const avatarText = computed(() => getIdentityInitial(post.value?.identity?.nickname || '星'))
const myAvatarText = computed(() => getIdentityInitial(authStore.identity?.nickname || '星'))
const canDirectMessage = computed(() => Boolean(post.value?.allow_messages) && !post.value?.is_author)
const replyTargetName = computed(() => {
  if (!replyTo.value) return ''
  return replyTo.value.is_post_author ? '楼主' : replyTo.value.anon_label
})
const reportTarget = ref<{ target_type: 'post' | 'comment'; target_id: number; label: string }>({
  target_type: 'post',
  target_id: postId.value,
  label: '帖子',
})

const commentTree = computed(() => {
  if (!flatComments.value.length) return []

  const nodeMap = new Map<number, any>()
  const roots: any[] = []

  flatComments.value.forEach((comment) => {
    nodeMap.set(comment.id, { ...comment, children: [] })
  })

  flatComments.value.forEach((comment) => {
    const node = nodeMap.get(comment.id)
    if (!node) return

    if (comment.parent) {
      const parentNode = nodeMap.get(comment.parent)
      if (parentNode) parentNode.children.push(node)
      else roots.push(node)
      return
    }

    roots.push(node)
  })

  return roots
})

function triggerBounce(target: typeof likeAnimating) {
  target.value = true
  setTimeout(() => { target.value = false }, 400)
}

function startEdit() {
  if (!post.value) return
  editContent.value = post.value.content
  editAllowMessages.value = post.value.allow_messages
  editPanelOpen.value = true
}

function resetPanels() {
  reportPanelOpen.value = false
  editPanelOpen.value = false
  messagePanelOpen.value = false
  showShareCard.value = false
  reportReason.value = ''
  reportDetail.value = ''
  messageDraft.value = ''
  reportTarget.value = {
    target_type: 'post',
    target_id: postId.value,
    label: '帖子',
  }
  replyTo.value = null
}

let syncTicket = 0

async function syncDetailPage() {
  if (!postId.value) {
    router.replace('/')
    return
  }

  const ticket = ++syncTicket
  loadingMessage.value = '详情页内容加载中，请稍候。'
  post.value = null
  flatComments.value = []
  commentText.value = ''
  resetPanels()

  try {
    const [postRes, commentsRes] = await Promise.all([
      postsApi.getDetail(postId.value),
      commentsApi.getList(postId.value),
    ])
    if (ticket !== syncTicket) return

    post.value = postRes.data.data
    flatComments.value = commentsRes.data.results || []
    await nextTick()
    await scrollToCommentsIfNeeded()
  } catch (error: any) {
    if (ticket !== syncTicket) return

    loadingMessage.value = error.response?.data?.message || '这颗气泡暂时无法接入。'
    if (error.response?.status === 404) {
      window.setTimeout(() => {
        if (route.name === 'PostDetail') {
          router.replace('/')
        }
      }, 900)
      return
    }

    toast.error(error.response?.data?.message || '帖子加载失败，请稍后重试')
  }
}

async function loadComments() {
  try {
    const res = await commentsApi.getList(postId.value)
    flatComments.value = res.data.results || []
  } catch {
    flatComments.value = []
  }
}

async function toggleLike() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }

  try {
    const res = await postsApi.toggleLike(postId.value)
    post.value.is_liked = res.data.data.is_liked
    post.value.like_count = res.data.data.like_count
    triggerBounce(likeAnimating)
    toast.success(post.value.is_liked ? '已点赞' : '已取消点赞')
  } catch {
    toast.error('点赞失败，请稍后重试')
  }
}

async function toggleFavorite() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }

  try {
    const res = await postsApi.toggleFavorite(postId.value)
    post.value.is_favorited = res.data.data.is_favorited
    post.value.favorite_count = res.data.data.favorite_count
    triggerBounce(favAnimating)
    toast.success(post.value.is_favorited ? '已收藏' : '已取消收藏')
  } catch {
    toast.error('收藏失败，请稍后重试')
  }
}

async function toggleCommentLike(commentId: number) {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }

  try {
    const res = await commentsApi.toggleLike(commentId)
    const target = flatComments.value.find((comment) => comment.id === commentId)
    if (!target) return
    target.is_liked = res.data.data.is_liked
    target.like_count = res.data.data.like_count
  } catch {
    toast.error('评论点赞失败，请稍后重试')
  }
}

async function scrollToCommentsIfNeeded() {
  await nextTick()
  if (route.hash !== '#comments') return
  commentsSectionRef.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

function startReply(comment: any) {
  replyTo.value = comment
}

function cancelReply() {
  replyTo.value = null
}

function openReportPanel(target_type: 'post' | 'comment', target_id: number, label: string) {
  reportTarget.value = { target_type, target_id, label }
  reportPanelOpen.value = true
}

function startReportComment(comment: any) {
  openReportPanel('comment', comment.id, `评论 #${comment.id}`)
}

async function submitComment() {
  const content = commentText.value.trim()
  if (!content || commentSubmitting.value) return

  commentSubmitting.value = true
  try {
    const res = await commentsApi.create(postId.value, {
      content,
      parent_id: replyTo.value?.id || null,
    })

    const successMessage = res.data.message || '评论发布成功'
    commentText.value = ''
    replyTo.value = null
    await loadComments()
    if (post.value) post.value.comment_count += 1

    toast.success(successMessage)
  } catch (error: any) {
    toast.error(error.response?.data?.message || '评论失败，请稍后再试')
  } finally {
    commentSubmitting.value = false
  }
}

async function deletePost() {
  try {
    await postsApi.delete(postId.value)
    toast.success('帖子已删除')
    router.push('/')
  } catch {
    toast.error('删除失败，请稍后重试')
  }
}

async function deleteComment(commentId: number) {
  try {
    await commentsApi.delete(commentId)
    await loadComments()
    if (post.value && post.value.comment_count > 0) {
      post.value.comment_count -= 1
    }
    toast.success('评论已删除')
  } catch {
    toast.error('删除评论失败，请稍后重试')
  }
}

async function submitReport() {
  if (!reportReason.value) return
  try {
    await postsApi.report({
      target_type: reportTarget.value.target_type,
      target_id: reportTarget.value.target_id,
      reason: reportReason.value,
      detail: reportDetail.value.trim(),
    })
    reportPanelOpen.value = false
    reportReason.value = ''
    reportDetail.value = ''
    toast.success(`${reportTarget.value.label}举报已提交，感谢你的反馈`)
    reportTarget.value = {
      target_type: 'post',
      target_id: postId.value,
      label: '帖子',
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || '举报提交失败')
  }
}

async function submitEdit() {
  if (!editContent.value.trim()) return
  try {
    const formData = new FormData()
    formData.append('content', editContent.value.trim())
    formData.append('allow_messages', String(editAllowMessages.value))
    const res = await postsApi.update(postId.value, formData)
    post.value = res.data.data
    editPanelOpen.value = false
    toast.success('帖子已更新')
  } catch (error: any) {
    toast.error(error.response?.data?.message || '编辑失败')
  }
}

async function votePoll(optionId: number) {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  try {
    const res = await postsApi.vote(postId.value, optionId)
    post.value = res.data.data
    toast.success('投票成功')
  } catch (error: any) {
    toast.error(error.response?.data?.message || '投票失败')
  }
}

function openMessageComposer() {
  if (!canDirectMessage.value) return
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  messagePanelOpen.value = true
}

function closeMessageComposer() {
  messagePanelOpen.value = false
  messageDraft.value = ''
}

async function submitDirectMessage() {
  const content = messageDraft.value.trim()
  if (!content || !canDirectMessage.value || messageSending.value) return

  messageSending.value = true
  try {
    const res = await messagesApi.sendMessage(postId.value, content)
    closeMessageComposer()
    toast.success('私信已发送')
    router.push(`/messages?tab=messages&conversation=${res.data.data.id}`)
  } catch (error: any) {
    toast.error(error.response?.data?.message || '私信发送失败')
  } finally {
    messageSending.value = false
  }
}

watch(
  () => route.hash,
  () => {
    scrollToCommentsIfNeeded()
  },
)

watch(
  () => route.params.id,
  async () => {
    window.scrollTo({ top: 0, behavior: 'auto' })
    await syncDetailPage()
  },
  { immediate: true },
)
</script>

<style scoped>
.detail-page {
  width: min(720px, 100%);
  margin: 0 auto;
  padding: 0 0 64px;
}

/* ===== POST CARD ===== */
.post-card {
  position: relative;
  border-radius: 28px;
  overflow: hidden;
  background: var(--glass-bg);
  border: 1px solid var(--border);
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-soft);
  animation: fade-in-up 0.5s ease;
}

.post-accent {
  height: 4px;
  border-radius: 4px 4px 0 0;
}

.accent-1 { background: linear-gradient(90deg, #ff6b9d, #ffa0c0); }
.accent-2 { background: linear-gradient(90deg, #ffa559, #ffc888); }
.accent-3 { background: linear-gradient(90deg, #06d6a0, #64e6b4); }
.accent-4 { background: linear-gradient(90deg, #64b4ff, #96c8ff); }
.accent-5 { background: linear-gradient(90deg, #7c5cfc, #b4a0ff); }
.accent-6 { background: linear-gradient(90deg, #ffe664, #fff096); }
.accent-7 { background: linear-gradient(90deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1)); }
.accent-8 { background: linear-gradient(90deg, #c8a078, #dcc08c); }

.post-inner {
  padding: 36px 32px;
}

.post-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.tag-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 16px;
  border-radius: var(--radius-pill);
  background: var(--bg-card);
  border: 1px solid var(--border);
  font-size: 0.875rem;
  font-weight: 600;
}

.destroy-hint {
  font-size: 0.75rem;
  color: var(--text-3);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  background: rgba(248, 113, 113, 0.08);
  border: 1px solid rgba(248, 113, 113, 0.15);
  color: var(--color-error);
}

.post-content {
  margin: 0;
  color: var(--text-1);
  font-size: 1.2rem;
  line-height: 1.9;
  letter-spacing: 0.02em;
  white-space: pre-wrap;
  word-break: break-word;
}

.post-images {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 24px;
}

.post-images img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: var(--radius-img);
  border: 1px solid var(--border);
}

.poll-card {
  margin-top: 24px;
  padding: 18px;
  border-radius: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
}

.poll-title {
  margin-bottom: 14px;
  font-weight: 600;
}

.poll-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.poll-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-1);
}

.poll-option.selected {
  border-color: rgba(124, 92, 252, 0.4);
  background: rgba(124, 92, 252, 0.12);
}

.post-footer {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--divider);
}

.author-avatar {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--gradient-brand);
  color: #fff;
  font-size: 1rem;
  font-weight: 700;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.author-name {
  color: var(--text-1);
  font-size: 0.9375rem;
  font-weight: 600;
}

.author-time,
.post-meta {
  color: var(--text-2);
  font-size: 0.8125rem;
}

.post-meta {
  text-align: right;
}

/* ===== ACTION BAR ===== */
.action-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 24px;
}

.action-pill {
  min-height: 42px;
  padding: 0 18px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border);
  background: var(--glass-bg);
  color: var(--text-2);
  backdrop-filter: blur(8px);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.action-pill:hover {
  color: var(--text-1);
  border-color: var(--border-hover);
  background: var(--bg-card-hover);
  transform: translateY(-1px);
}

.action-pill.active {
  color: var(--pink);
  border-color: rgba(255, 107, 157, 0.3);
  background: rgba(255, 107, 157, 0.08);
}

.action-pill.dm {
  color: var(--cyan);
  border-color: rgba(6, 214, 160, 0.3);
}

.action-pill:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-pill.danger:hover {
  color: var(--color-error);
}

.action-icon {
  display: inline-block;
}

/* ===== FLOATING PANELS ===== */
.floating-panel {
  margin: 18px auto 0;
  padding: 20px;
  border-radius: 22px;
  animation: fade-in-up 0.3s ease;
}

.panel-head,
.panel-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-head button {
  border: 0;
  background: transparent;
  color: var(--text-2);
}

.panel-head button:hover {
  color: var(--text-1);
}

.reason-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0;
}

.reason-chips :deep(.active) {
  color: #fff;
  background: var(--brand);
  border-color: transparent;
}

.panel-subtitle {
  margin: 6px 0 0;
  color: var(--text-3);
  font-size: 0.85rem;
}

.message-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 14px 0;
  color: var(--text-2);
  font-size: 0.85rem;
}

.message-tags span {
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: var(--bg-card);
  border: 1px solid var(--border);
}

.floating-panel textarea {
  width: 100%;
  min-height: 88px;
  margin-bottom: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-1);
  resize: vertical;
}

.floating-panel textarea:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--glow-brand);
  outline: none;
}

.edit-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0;
  color: var(--text-2);
  font-size: 0.875rem;
}

/* ===== COMMENTS SECTION ===== */
.comments-section {
  margin-top: 40px;
  animation: fade-in-up 0.5s ease 0.15s both;
}

.comments-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.comments-title h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
}

.comments-count {
  font-size: 0.875rem;
  color: var(--text-3);
}

/* Comment List */
.comment-list {
  margin-top: 8px;
}

.login-hint {
  padding: 20px;
  border-radius: 20px;
  background: var(--glass-bg-muted);
  border: 1px solid var(--border);
  color: var(--text-2);
  margin-bottom: 24px;
}

.empty-comments {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-3);
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* Loading */
.loading-wrap {
  padding: 40px 0 12px;
}

.loading-card {
  width: min(560px, 100%);
  margin: 0 auto;
  padding: 40px 24px;
  border-radius: 24px;
  text-align: center;
  background: var(--glass-bg-muted);
  border: 1px solid var(--border);
  backdrop-filter: blur(18px);
}

.loading-card h3 {
  margin: 0 0 10px;
  font-size: 1.125rem;
}

.loading-card p {
  margin: 0;
  color: var(--text-2);
}

.spinner {
  width: 32px;
  height: 32px;
  margin: 0 auto 16px;
  border: 3px solid var(--border);
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .detail-page {
    width: 100%;
  }

  .post-inner {
    padding: 24px 20px;
  }

  .post-content {
    font-size: 1.0625rem;
  }

  .post-footer {
    flex-wrap: wrap;
  }

  .post-meta {
    width: 100%;
    text-align: left;
  }

  .action-bar {
    gap: 8px;
  }

  .action-pill {
    padding: 0 14px;
    min-height: 38px;
    font-size: 0.8125rem;
  }
}
</style>
