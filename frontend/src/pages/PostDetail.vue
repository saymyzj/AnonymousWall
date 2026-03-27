<template>
  <div v-if="post" class="detail-page">
    <article class="post-bubble bubble-surface" :class="bubbleClass">
      <div class="bubble-header">
        <span class="tag-label">{{ tagEmoji(post.tag) }} {{ post.tag }}</span>
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
          {{ post.comment_count }} 条评论 · {{ post.favorite_count }} 次收藏
        </span>
      </div>
    </article>

    <div class="action-bar">
      <button class="action-pill" :class="{ active: post.is_liked }" type="button" @click="toggleLike">
        {{ post.is_liked ? '❤️' : '♡' }} {{ post.like_count }}
      </button>
      <button class="action-pill" :class="{ active: post.is_favorited }" type="button" @click="toggleFavorite">
        ⭐ {{ post.favorite_count }}
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

    <Transition name="hint-fade">
      <GlassCard v-if="actionNotice" class="action-notice">
        {{ actionNotice }}
      </GlassCard>
    </Transition>

    <GlassCard v-if="reportPanelOpen" class="report-panel">
      <div class="report-header">
        <strong>举报{{ reportTarget.label }}</strong>
        <button type="button" @click="reportPanelOpen = false">关闭</button>
      </div>
      <div class="report-reasons">
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
      <div class="report-footer">
        <span>{{ reportDetail.length }} / 100</span>
        <button class="pill-button brand" type="button" :disabled="!reportReason" @click="submitReport">提交举报</button>
      </div>
    </GlassCard>

    <GlassCard v-if="editPanelOpen" class="report-panel">
      <div class="report-header">
        <strong>编辑帖子</strong>
        <button type="button" @click="editPanelOpen = false">关闭</button>
      </div>
      <textarea v-model="editContent" maxlength="500" placeholder="修改帖子内容"></textarea>
      <label class="edit-toggle">
        <input v-model="editAllowMessages" type="checkbox" />
        <span>允许匿名私信</span>
      </label>
      <div class="report-footer">
        <span>{{ editContent.length }} / 500</span>
        <button class="pill-button brand" type="button" :disabled="!editContent.trim()" @click="submitEdit">保存修改</button>
      </div>
    </GlassCard>

    <GlassCard v-if="messagePanelOpen" class="report-panel">
      <div class="report-header">
        <div>
          <strong>发送匿名私信</strong>
          <p class="panel-subtitle">消息会进入私信中心，楼主回复后你也能继续在会话里交流。</p>
        </div>
        <button type="button" @click="closeMessageComposer">关闭</button>
      </div>
      <div class="message-summary">
        <span>发送对象：{{ post.identity?.nickname || '匿名楼主' }}</span>
        <span>关联帖子：{{ post.tag }}</span>
      </div>
      <textarea
        v-model="messageDraft"
        maxlength="300"
        placeholder="写下你想悄悄说的话，支持 300 字以内。"
      ></textarea>
      <div class="report-footer">
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

    <section id="comments" ref="commentsSectionRef" class="comments-section">
      <div class="section-heading">
        <h3>评论</h3>
        <span class="meta">{{ post.comment_count }}</span>
      </div>

      <GlassCard
        v-if="authStore.isLoggedIn && authStore.isVerified"
        class="comment-input-card"
      >
        <div class="input-header">
          <div class="input-avatar">{{ avatarText }}</div>
          <span class="input-hint">以匿名身份评论</span>
        </div>

        <div v-if="replyTo" class="reply-hint">
          <span>正在回复 {{ replyTo.is_post_author ? '楼主' : replyTo.anon_label }}</span>
          <button type="button" @click="replyTo = null">取消</button>
        </div>

        <textarea
          ref="commentInputEl"
          v-model="commentText"
          maxlength="200"
          placeholder="写下你的评论..."
          @keydown.enter.exact.prevent="submitComment"
        ></textarea>

        <div class="input-toolbar">
          <span class="char-count">{{ commentText.length }} / 200</span>
          <button class="submit-btn" type="button" :disabled="!commentText.trim() || commentSubmitting" @click="submitComment">
            {{ commentSubmitting ? '发布中...' : '发布' }}
          </button>
        </div>
      </GlassCard>

      <GlassCard v-else class="login-hint-card" muted>
        登录并完成认证后，就可以在这里留下你的匿名回应。
      </GlassCard>

      <div v-if="commentTree.length" class="comment-list">
        <CommentTree
          v-for="comment in commentTree"
          :key="comment.id"
          :comment="comment"
          :depth="0"
          @reply="startReply"
          @like="toggleCommentLike"
          @delete="deleteComment"
          @report="startReportComment"
        />
      </div>

      <GlassCard v-else class="empty-comments" muted>
        第一条评论，会成为这颗气泡的第一束回声。
      </GlassCard>
    </section>
  </div>

  <div v-else class="loading-wrap">
    <GlassCard class="status-card">
      <div class="spinner"></div>
      <h3>正在接入这颗气泡</h3>
      <p>{{ loadingMessage }}</p>
    </GlassCard>
  </div>

  <ShareCardModal v-if="showShareCard && post" :post="post" @close="showShareCard = false" />
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommentTree from '../components/CommentTree.vue'
import GlassCard from '../components/GlassCard.vue'
import ShareCardModal from '../components/ShareCardModal.vue'
import { commentsApi } from '../api/comments'
import { messagesApi } from '../api/messages'
import { postsApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'
import { formatTimeAgo, getIdentityInitial, tagEmoji } from '../utils/presentation'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const post = ref<any>(null)
const flatComments = ref<any[]>([])
const commentText = ref('')
const commentSubmitting = ref(false)
const replyTo = ref<any>(null)
const actionNotice = ref('')
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
const commentInputEl = ref<HTMLTextAreaElement>()
const commentsSectionRef = ref<HTMLElement>()
const reportReasons = ['广告引流', '人身攻击', '色情低俗', '隐私泄露', '其他']

const postId = computed(() => Number(route.params.id))
const bubbleClass = computed(() => `bubble-${post.value?.bg_color || 7}`)
const avatarText = computed(() => getIdentityInitial(post.value?.identity?.nickname || '星'))
const canDirectMessage = computed(() => Boolean(post.value?.allow_messages) && !post.value?.is_author)
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

function autoGrowTextarea() {
  if (!commentInputEl.value) return
  commentInputEl.value.style.height = 'auto'
  commentInputEl.value.style.height = `${Math.min(commentInputEl.value.scrollHeight, 160)}px`
}

function clearActionNoticeSoon() {
  window.setTimeout(() => {
    actionNotice.value = ''
  }, 2200)
}

function showPendingFeature(message: string) {
  actionNotice.value = message
  clearActionNoticeSoon()
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
    autoGrowTextarea()
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

    actionNotice.value = error.response?.data?.message || '帖子加载失败，请稍后重试'
    clearActionNoticeSoon()
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
  } catch {
    showPendingFeature('点赞失败，请稍后重试')
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
  } catch {
    showPendingFeature('收藏失败，请稍后重试')
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
    showPendingFeature('评论点赞失败，请稍后重试')
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
  nextTick(() => {
    commentInputEl.value?.focus()
    autoGrowTextarea()
  })
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

    await nextTick()
    autoGrowTextarea()
    showPendingFeature(successMessage)
  } catch (error: any) {
    actionNotice.value = error.response?.data?.message || '评论失败，请稍后再试'
    clearActionNoticeSoon()
  } finally {
    commentSubmitting.value = false
  }
}

async function deletePost() {
  try {
    await postsApi.delete(postId.value)
    router.push('/')
  } catch {
    showPendingFeature('删除失败，请稍后重试')
  }
}

async function deleteComment(commentId: number) {
  try {
    await commentsApi.delete(commentId)
    await loadComments()
    if (post.value && post.value.comment_count > 0) {
      post.value.comment_count -= 1
    }
  } catch {
    showPendingFeature('删除评论失败，请稍后重试')
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
    showPendingFeature(`${reportTarget.value.label}举报已提交，感谢你的反馈`)
    reportTarget.value = {
      target_type: 'post',
      target_id: postId.value,
      label: '帖子',
    }
  } catch (error: any) {
    showPendingFeature(error.response?.data?.message || '举报提交失败')
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
    showPendingFeature('帖子已更新')
  } catch (error: any) {
    showPendingFeature(error.response?.data?.message || '编辑失败')
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
  } catch (error: any) {
    showPendingFeature(error.response?.data?.message || '投票失败')
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
    router.push(`/messages?tab=messages&conversation=${res.data.data.id}`)
  } catch (error: any) {
    showPendingFeature(error.response?.data?.message || '私信发送失败')
  } finally {
    messageSending.value = false
  }
}

watch(commentText, async () => {
  await nextTick()
  autoGrowTextarea()
})

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

.post-bubble {
  border-radius: 28px;
  padding: 40px 36px;
}

.post-bubble::after {
  content: '';
  position: absolute;
  bottom: -16px;
  left: 50%;
  width: 40px;
  height: 4px;
  transform: translateX(-50%);
  border-radius: 999px;
  background: var(--bubble-decor, rgba(255, 255, 255, 0.22));
}

.bubble-header {
  margin-bottom: 18px;
}

.tag-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 16px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.875rem;
  font-weight: 600;
}

.post-content {
  margin: 0;
  color: var(--text-1);
  font-size: 1.25rem;
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
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.poll-card {
  margin-top: 24px;
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
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
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
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
  border-top: 1px solid rgba(255, 255, 255, 0.06);
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

.action-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 28px;
}

.action-pill {
  min-height: 44px;
  padding: 0 20px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-2);
}

.action-pill:hover {
  color: var(--text-1);
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.1);
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

.action-notice {
  margin: 18px auto 0;
  padding: 14px 18px;
  width: fit-content;
  max-width: 100%;
  border-radius: 18px;
  color: var(--text-2);
}

.report-panel {
  margin: 18px auto 0;
  padding: 18px;
  border-radius: 20px;
}

.report-header,
.report-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.report-header button {
  border: 0;
  background: transparent;
  color: var(--text-2);
}

.report-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0;
}

.report-reasons :deep(.active) {
  color: #fff;
  background: var(--brand);
  border-color: transparent;
}

.panel-subtitle {
  margin: 6px 0 0;
  color: var(--text-3);
  font-size: 0.85rem;
}

.message-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 14px 0;
  color: var(--text-2);
  font-size: 0.85rem;
}

.message-summary span {
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.report-panel textarea {
  width: 100%;
  min-height: 88px;
  margin-bottom: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-1);
  resize: vertical;
}

.edit-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0;
  color: var(--text-2);
  font-size: 0.875rem;
}

.comments-section {
  margin-top: 40px;
}

.comment-input-card,
.login-hint-card,
.empty-comments {
  margin-top: 20px;
  padding: 20px;
  border-radius: 20px;
}

.comment-input-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-input-card:deep(.glass-card) {
  width: 100%;
}

.input-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.input-avatar {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--gradient-avatar);
  color: #fff;
  font-weight: 700;
}

.input-hint {
  color: var(--text-2);
  font-size: 0.875rem;
}

.reply-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--brand);
  font-size: 0.8125rem;
}

.reply-hint button {
  border: 0;
  background: transparent;
  color: var(--text-2);
}

.reply-hint button:hover {
  color: var(--text-1);
}

.comment-input-card textarea {
  width: 100%;
  min-height: 48px;
  max-height: 160px;
  padding: 2px 0 12px;
  border: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: transparent;
  color: var(--text-1);
  line-height: 1.7;
  resize: none;
  outline: none;
  overflow-y: auto;
}

.comment-input-card textarea::placeholder {
  color: var(--text-3);
}

.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  color: var(--text-3);
  font-size: 0.75rem;
}

.submit-btn {
  min-height: 36px;
  padding: 0 22px;
  border: 0;
  border-radius: var(--radius-pill);
  background: var(--brand);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 8px 20px rgba(124, 92, 252, 0.18);
}

.submit-btn:hover:not(:disabled) {
  background: var(--brand-deep);
}

.submit-btn:disabled {
  opacity: 0.45;
}

.comment-list {
  margin-top: 28px;
}

.login-hint-card,
.empty-comments {
  color: var(--text-2);
}

.loading-wrap {
  padding: 40px 0 12px;
}

.spinner {
  width: 32px;
  height: 32px;
  margin: 0 auto 16px;
  border: 3px solid rgba(255, 255, 255, 0.08);
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.hint-fade-enter-active,
.hint-fade-leave-active {
  transition: opacity 0.2s ease;
}

.hint-fade-enter-from,
.hint-fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .detail-page {
    width: 100%;
  }

  .post-bubble {
    padding: 28px 24px;
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
}
</style>
