<template>
  <div class="profile-page">
    <!-- Top Banner -->
    <div class="profile-banner">
      <div class="banner-left">
        <div class="avatar-lg" :style="{ background: avatarColor }">
          {{ avatarText }}
        </div>
        <div class="user-info">
          <h2>{{ authStore.identity?.nickname || '匿名用户' }}</h2>
          <div class="user-meta">
            <span class="verify-badge" :class="{ verified: authStore.isVerified }">
              {{ authStore.isVerified ? '已验证' : '审核中' }}
            </span>
            <span class="join-date">注册于 {{ formatDate(authStore.userInfo?.date_joined) }}</span>
          </div>
        </div>
      </div>
      <div class="stats-row">
        <div class="stat">
          <span class="stat-num">{{ myPosts.length }}</span>
          <span class="stat-label">发布</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ totalLikes }}</span>
          <span class="stat-label">获赞</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ totalComments }}</span>
          <span class="stat-label">评论</span>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'posts' }"
        @click="activeTab = 'posts'"
      >
        我的发布
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'comments' }"
        @click="activeTab = 'comments'"
      >
        我的评论
      </button>
      <div class="tab-indicator" :style="{ transform: activeTab === 'posts' ? 'translateX(0)' : 'translateX(100%)' }"></div>
    </div>

    <!-- Content -->
    <div class="content-area">
      <template v-if="activeTab === 'posts'">
        <div v-if="myPosts.length > 0" class="posts-grid">
          <PostCard v-for="p in myPosts" :key="p.id" :post="p" />
        </div>
        <div v-else class="empty-state">
          <p>还没有发布过内容</p>
        </div>
      </template>

      <template v-if="activeTab === 'comments'">
        <div class="empty-state">
          <p>即将上线</p>
        </div>
      </template>
    </div>

    <!-- Logout -->
    <div class="logout-area">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { postsApi } from '../api/posts'
import PostCard from '../components/PostCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const myPosts = ref<any[]>([])
const activeTab = ref<'posts' | 'comments'>('posts')

const avatarColor = computed(() => {
  const seed = authStore.identity?.avatar_seed || '777777'
  return `#${seed.substring(0, 6)}`
})

const avatarText = computed(() => {
  const nick = authStore.identity?.nickname || '?'
  return nick.charAt(2) || nick.charAt(0)
})

const totalLikes = computed(() =>
  myPosts.value.reduce((sum: number, p: any) => sum + (p.like_count || 0), 0)
)

const totalComments = computed(() =>
  myPosts.value.reduce((sum: number, p: any) => sum + (p.comment_count || 0), 0)
)

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  if (!authStore.userInfo) await authStore.fetchMe()
  try {
    const res = await postsApi.getList({})
    myPosts.value = (res.data.results || []).filter((p: any) => p.is_author)
  } catch { /* ignore */ }
})
</script>

<style scoped>
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
}

/* Banner */
.profile-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32px 36px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 28px;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-lg {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.user-info h2 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 6px;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.verify-badge {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.1);
  color: var(--color-warning);
  font-weight: 500;
}

.verify-badge.verified {
  background: rgba(52, 211, 153, 0.1);
  color: var(--color-success);
}

.join-date {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Stats */
.stats-row {
  display: flex;
  gap: 32px;
}

.stat {
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-primary);
  line-height: 1.2;
}

.stat-label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

/* Tabs */
.tab-bar {
  display: flex;
  position: relative;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--divider);
}

.tab-btn {
  flex: 0 0 auto;
  padding: 12px 32px;
  background: none;
  border: none;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s;
  position: relative;
}

.tab-btn:hover {
  color: var(--brand-primary);
  transform: none;
}

.tab-btn.active {
  color: var(--brand-primary);
  font-weight: 600;
}

.tab-indicator {
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 50%;
  height: 2px;
  background: var(--brand-primary);
  border-radius: 1px;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Content */
.posts-grid {
  column-count: 3;
  column-gap: 24px;
}

.posts-grid > :deep(*) {
  break-inside: avoid;
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 64px 0;
  color: var(--text-placeholder);
  font-size: 15px;
  background: white;
  border-radius: 20px;
}

/* Logout */
.logout-area {
  margin-top: 40px;
  text-align: center;
}

.logout-btn {
  background: none;
  border: 1.5px solid var(--divider);
  border-radius: 20px;
  padding: 10px 32px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  border-color: var(--color-error);
  color: var(--color-error);
  transform: none;
}
</style>
