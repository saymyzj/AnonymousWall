<template>
  <div class="profile-page">
    <div class="profile-grid">
      <!-- Left Sidebar: User Info -->
      <aside class="sidebar">
        <div class="profile-card">
          <div class="avatar-lg" :style="{ background: avatarColor }">
            {{ avatarText }}
          </div>
          <h2>{{ authStore.identity?.nickname || '匿名用户' }}</h2>
          <p class="verify-status" :class="{ verified: authStore.isVerified }">
            {{ authStore.isVerified ? '已验证' : '审核中' }}
          </p>
          <p class="join-date">注册于 {{ formatDate(authStore.userInfo?.date_joined) }}</p>
        </div>

        <!-- Stats Cards -->
        <div class="stats-row">
          <div class="stat-card">
            <span class="stat-number">{{ myPosts.length }}</span>
            <span class="stat-label">发布</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ totalComments }}</span>
            <span class="stat-label">评论</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ totalLikes }}</span>
            <span class="stat-label">获赞</span>
          </div>
        </div>

        <!-- Menu -->
        <div class="menu-card">
          <div class="menu-item" :class="{ active: activeTab === 'posts' }" @click="activeTab = 'posts'">
            <span>📝 我的发布</span>
          </div>
          <div class="menu-item" :class="{ active: activeTab === 'comments' }" @click="activeTab = 'comments'">
            <span>💬 我的评论</span>
          </div>
          <div class="menu-item logout" @click="handleLogout">
            <span>🚪 退出登录</span>
          </div>
        </div>
      </aside>

      <!-- Right: Content Area -->
      <div class="content-area">
        <h3 class="content-title">{{ activeTab === 'posts' ? '我的发布' : '我的评论' }}</h3>

        <!-- My Posts -->
        <template v-if="activeTab === 'posts'">
          <div v-if="myPosts.length > 0" class="my-posts-grid">
            <PostCard
              v-for="p in myPosts"
              :key="p.id"
              :post="p"
            />
          </div>
          <div v-else class="empty">
            <p>还没有发布过内容</p>
          </div>
        </template>

        <!-- My Comments (placeholder) -->
        <template v-if="activeTab === 'comments'">
          <div class="empty">
            <p>即将上线</p>
          </div>
        </template>
      </div>
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

const totalLikes = computed(() => {
  return myPosts.value.reduce((sum: number, p: any) => sum + (p.like_count || 0), 0)
})

const totalComments = computed(() => {
  return myPosts.value.reduce((sum: number, p: any) => sum + (p.comment_count || 0), 0)
})

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  if (!authStore.userInfo) {
    await authStore.fetchMe()
  }
  try {
    const res = await postsApi.getList({})
    myPosts.value = (res.data.results || []).filter(
      (p: any) => p.is_author
    )
  } catch { /* ignore */ }
})
</script>

<style scoped>
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-5);
}

@media (min-width: 768px) {
  .profile-grid {
    grid-template-columns: 280px 1fr;
    gap: var(--space-8);
    align-items: start;
  }

  .sidebar {
    position: sticky;
    top: 80px;
  }
}

/* Profile Card */
.profile-card {
  text-align: center;
  padding: var(--space-6);
  background: var(--card-bg);
  border-radius: var(--card-radius);
  margin-bottom: var(--space-4);
}

.avatar-lg {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto var(--space-3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.profile-card h2 {
  font-size: 20px;
  margin-bottom: var(--space-1);
}

.verify-status {
  font-size: 13px;
  color: var(--color-warning);
  margin-bottom: var(--space-1);
}

.verify-status.verified {
  color: var(--color-success);
}

.join-date {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.stat-card {
  text-align: center;
  padding: var(--space-3);
  background: var(--card-bg);
  border-radius: 16px;
}

.stat-number {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: var(--brand-primary);
  line-height: 1.2;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

/* Menu */
.menu-card {
  background: var(--card-bg);
  border-radius: 20px;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  border-left: 3px solid transparent;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background: var(--brand-primary-light);
}

.menu-item.active {
  border-left-color: var(--brand-primary);
  color: var(--brand-primary);
  font-weight: 600;
  background: var(--brand-primary-light);
}

.menu-item.logout {
  color: var(--color-error);
  border-top: 1px solid var(--divider);
}

.menu-item.logout:hover {
  background: rgba(248, 113, 113, 0.08);
}

/* Content Area */
.content-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: var(--space-4);
}

.my-posts-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

@media (min-width: 768px) {
  .my-posts-grid {
    display: block;
    column-count: 2;
    column-gap: 16px;
  }

  .my-posts-grid > :deep(*) {
    break-inside: avoid;
    margin-bottom: 12px;
  }
}

.empty {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--space-10) 0;
  background: var(--card-bg);
  border-radius: var(--card-radius);
}

.empty p {
  font-size: 15px;
}
</style>
