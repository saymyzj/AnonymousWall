<template>
  <div class="messages-page">
    <div class="split-container">
      <aside class="left-panel">
        <div class="left-header">
          <div class="left-tabs">
            <button class="left-tab" :class="{ active: activeTab === 'messages' }" type="button" @click="activeTab = 'messages'">
              私信
              <span v-if="totalUnreadMessages > 0" class="cnt">{{ totalUnreadMessages }}</span>
            </button>
            <button class="left-tab" :class="{ active: activeTab === 'notifications' }" type="button" @click="activeTab = 'notifications'">
              通知
              <span v-if="totalUnreadNotifications > 0" class="cnt">{{ totalUnreadNotifications }}</span>
            </button>
          </div>
          <button class="mark-all-btn" type="button" @click="markAllAsRead">全部标为已读</button>
        </div>

        <div class="left-scroll">
          <template v-if="activeTab === 'messages'">
            <button
              v-for="conversation in conversations"
              :key="conversation.id"
              class="lp-pm"
              :class="{ active: activeConversationId === conversation.id }"
              type="button"
              @click="activeConversationId = conversation.id"
            >
              <div class="lp-pm-avatar" :class="conversation.avatar_class">{{ conversation.avatar }}</div>
              <div class="lp-pm-body">
                <div class="lp-pm-row">
                  <span class="lp-pm-name">{{ conversation.name }}</span>
                  <span class="lp-pm-time">{{ conversation.time }}</span>
                </div>
                <div class="lp-pm-preview">{{ conversation.preview }}</div>
              </div>
              <span v-if="conversation.unread" class="lp-pm-badge">{{ conversation.unread }}</span>
            </button>
            <div v-if="!conversations.length" class="empty-list">还没有私信会话</div>
          </template>

          <template v-else>
            <template v-for="group in notificationGroups" :key="group.label">
              <div class="group-title">{{ group.label }}</div>
              <div
                v-for="notification in group.items"
                :key="notification.id"
                class="lp-notif"
                :class="{ unread: !notification.is_read, active: activeNotificationId === notification.id }"
                @click="activeNotificationId = notification.id"
              >
                <div class="lp-icon" :class="notification.type">{{ notification.icon }}</div>
                <div class="lp-text">
                  <strong>{{ notification.title }}</strong>
                  <div>{{ notification.content }}</div>
                  <span class="time">{{ notification.time }}</span>
                </div>
              </div>
            </template>
            <div v-if="!notifications.length" class="empty-list">还没有通知</div>
          </template>
        </div>
      </aside>

      <section class="right-panel">
        <template v-if="activeTab === 'messages'">
          <div v-if="currentConversation" class="chat-view">
            <div class="chat-topbar">
              <div>
                <div class="chat-name">{{ currentConversation.name }}</div>
                <div class="chat-ref">关联帖子 · {{ currentConversation.post_ref.slice(0, 22) || '原帖' }}</div>
              </div>
              <div class="chat-toolbar">
                <router-link class="chat-link" :to="currentConversation.post_link">查看原帖</router-link>
                <button v-if="isConversationOwner" class="ghost-pill" type="button" @click="blockConversation">关闭会话</button>
              </div>
            </div>
            <div class="chat-messages">
              <div class="chat-time-group">会话记录</div>
              <div
                v-for="message in currentConversation.messages"
                :key="message.id"
                class="chat-msg"
                :class="message.mine ? 'me' : 'them'"
              >
                {{ message.content }}
              </div>
            </div>
            <div class="chat-input-area">
              <textarea v-model="messageDraft" placeholder="输入一条匿名消息..." maxlength="300"></textarea>
              <div class="chat-actions">
                <span>{{ messageDraft.length }} / 300</span>
                <button class="pill-button brand" type="button" :disabled="!messageDraft.trim()" @click="replyMessage">发送</button>
              </div>
            </div>
          </div>
          <div v-else class="empty-detail">选择一个会话开始查看。</div>
        </template>

        <template v-else>
          <div class="detail-notif">
            <GlassCard v-if="currentNotification" class="notif-detail-card">
              <div class="notif-title">{{ currentNotification.title }}</div>
              <p class="notif-body">{{ currentNotification.content }}</p>
              <div class="notif-actions">
                <router-link class="ghost-pill" :to="currentNotification.link || '/'">查看相关内容</router-link>
                <button class="ghost-pill" type="button" @click="ignoreNotification(currentNotification.id)">忽略</button>
              </div>
            </GlassCard>
            <div v-else class="empty-detail">没有可查看的通知。</div>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import GlassCard from '../components/GlassCard.vue'
import { messagesApi } from '../api/messages'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const activeTab = ref((route.query.tab as 'messages' | 'notifications') || 'messages')
const activeConversationId = ref<number | null>((route.query.conversation ? Number(route.query.conversation) : null))
const activeNotificationId = ref<number | null>(null)
const conversations = ref<any[]>([])
const notifications = ref<any[]>([])
const messageDraft = ref('')

const notificationGroups = computed(() => {
  const groups: Record<string, any[]> = {}
  notifications.value.forEach((item) => {
    if (!groups[item.group]) groups[item.group] = []
    groups[item.group].push(item)
  })
  return Object.entries(groups).map(([label, items]) => ({ label, items }))
})

const totalUnreadMessages = computed(() => conversations.value.reduce((sum, item) => sum + (item.unread || 0), 0))
const totalUnreadNotifications = computed(() => notifications.value.filter((item) => !item.is_read).length)

const currentConversation = computed(() => conversations.value.find((item) => item.id === activeConversationId.value) || null)
const currentNotification = computed(() => notifications.value.find((item) => item.id === activeNotificationId.value) || null)
const isConversationOwner = computed(() => currentConversation.value?.owner_id === authStore.userInfo?.id)

async function loadData() {
  const [conversationRes, notificationRes] = await Promise.all([
    messagesApi.getConversations(),
    messagesApi.getNotifications(),
  ])
  conversations.value = conversationRes.data.data.conversations || []
  notifications.value = notificationRes.data.data || []
  activeConversationId.value = activeConversationId.value || conversations.value[0]?.id || null
  activeNotificationId.value = activeNotificationId.value || notifications.value[0]?.id || null
}

async function markAllAsRead() {
  await messagesApi.markAllRead()
  await loadData()
}

async function ignoreNotification(id: number) {
  await messagesApi.ignoreNotification(id)
  await loadData()
}

async function replyMessage() {
  if (!currentConversation.value || !messageDraft.value.trim()) return
  await messagesApi.replyMessage(currentConversation.value.id, messageDraft.value.trim())
  messageDraft.value = ''
  await loadData()
}

async function blockConversation() {
  if (!currentConversation.value) return
  await messagesApi.blockConversation(currentConversation.value.id)
  await loadData()
}

watch(
  () => route.query.tab,
  (value) => {
    if (value === 'notifications' || value === 'messages') {
      activeTab.value = value
    }
  },
)

watch(
  () => route.query.conversation,
  (value) => {
    if (value) activeConversationId.value = Number(value)
  },
)

onMounted(loadData)
</script>

<style scoped>
.messages-page {
  min-height: calc(100vh - 120px);
}

.split-container {
  display: flex;
  min-height: calc(100vh - 120px);
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
}

.left-panel {
  width: 320px;
  flex-shrink: 0;
  background: rgba(11, 13, 26, 0.5);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
}

.left-header {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}

.left-tabs {
  display: flex;
  gap: 4px;
  padding: 3px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.04);
}

.left-tab {
  flex: 1;
  min-height: 36px;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--text-2);
  font-weight: 600;
}

.left-tab.active {
  background: var(--brand);
  color: #fff;
}

.cnt {
  margin-left: 6px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  background: var(--pink);
  color: #fff;
  font-size: 0.625rem;
}

.mark-all-btn {
  border: 0;
  background: transparent;
  color: var(--text-3);
  text-align: right;
}

.left-scroll {
  flex: 1;
  overflow: auto;
}

.empty-list,
.empty-detail {
  padding: 24px;
  color: var(--text-3);
}

.group-title {
  padding: 12px 16px 6px;
  color: var(--text-3);
  font-size: 0.75rem;
  font-weight: 600;
}

.lp-pm,
.lp-notif {
  width: 100%;
  padding: 12px 16px;
  border: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.lp-pm.active,
.lp-notif.active {
  background: rgba(124, 92, 252, 0.08);
  border-left: 3px solid var(--brand);
}

.lp-pm {
  display: flex;
  align-items: center;
  gap: 10px;
}

.lp-pm-avatar,
.lp-icon {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
}

.lp-pm-avatar.a1 { background: linear-gradient(135deg, rgba(124,92,252,0.2), rgba(124,92,252,0.1)); }
.lp-pm-avatar.a2 { background: linear-gradient(135deg, rgba(255,107,157,0.2), rgba(255,107,157,0.1)); }
.lp-pm-avatar.a3 { background: linear-gradient(135deg, rgba(6,214,160,0.2), rgba(6,214,160,0.1)); }

.lp-pm-body {
  min-width: 0;
  flex: 1;
}

.lp-pm-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.lp-pm-name {
  font-size: 0.8125rem;
  font-weight: 600;
}

.lp-pm-time,
.lp-pm-preview {
  color: var(--text-3);
  font-size: 0.75rem;
}

.lp-pm-preview {
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lp-pm-badge {
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  background: var(--brand);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
}

.lp-notif {
  display: flex;
  gap: 10px;
}

.lp-icon.comment { background: rgba(124,92,252,0.15); }
.lp-icon.like { background: rgba(255,107,157,0.15); }
.lp-icon.report { background: rgba(255,159,67,0.15); }
.lp-icon.system { background: rgba(6,214,160,0.15); }
.lp-icon.message { background: rgba(6,214,160,0.15); }
.lp-icon.favorite { background: rgba(255,230,100,0.15); }

.lp-text {
  flex: 1;
  min-width: 0;
  color: var(--text-2);
  font-size: 0.8125rem;
}

.lp-text strong {
  display: block;
  margin-bottom: 2px;
  color: var(--text-1);
}

.lp-text .time {
  display: block;
  margin-top: 4px;
  color: var(--text-3);
  font-size: 0.75rem;
}

.lp-notif.unread::after {
  content: '';
  width: 7px;
  height: 7px;
  border-radius: 50%;
  align-self: center;
  background: var(--brand);
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-view {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.chat-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
}

.chat-name {
  font-size: 0.9375rem;
  font-weight: 600;
}

.chat-ref {
  color: var(--text-3);
  font-size: 0.75rem;
}

.chat-toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
}

.chat-link {
  color: var(--cyan);
  font-size: 0.8125rem;
}

.chat-messages {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 24px;
}

.chat-time-group {
  text-align: center;
  color: var(--text-3);
  font-size: 0.75rem;
}

.chat-msg {
  max-width: 68%;
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.6;
}

.chat-msg.them {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  border-bottom-left-radius: 6px;
}

.chat-msg.me {
  align-self: flex-end;
  background: linear-gradient(135deg, var(--brand), #9b7dff);
  color: #fff;
  border-bottom-right-radius: 6px;
}

.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid var(--border);
}

.chat-input-area textarea {
  width: 100%;
  min-height: 88px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-1);
  resize: none;
}

.chat-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: var(--text-3);
  font-size: 0.75rem;
}

.detail-notif {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.notif-detail-card {
  width: min(520px, 100%);
  padding: 28px;
  border-radius: 24px;
}

.notif-title {
  margin-bottom: 12px;
  font-size: 1.1rem;
  font-weight: 700;
}

.notif-body {
  margin: 0;
  color: var(--text-2);
  line-height: 1.7;
}

.notif-actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

@media (max-width: 768px) {
  .split-container {
    flex-direction: column;
  }

  .left-panel {
    width: 100%;
    max-height: 360px;
  }
}
</style>
