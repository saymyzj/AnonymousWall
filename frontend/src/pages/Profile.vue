<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="avatar-lg" :style="{ background: avatarColor }">
        {{ avatarText }}
      </div>
      <h2>{{ authStore.identity?.nickname || '匿名用户' }}</h2>
      <p class="join-date">注册于 {{ formatDate(authStore.userInfo?.date_joined) }}</p>
    </div>

    <div class="menu-card">
      <div class="menu-item" @click="showMyPosts = true">
        <span>📝 我的发布</span>
        <span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="handleLogout">
        <span>🚪 退出登录</span>
        <span class="arrow">›</span>
      </div>
    </div>

    <!-- My Posts Popup -->
    <van-popup v-model:show="showMyPosts" position="bottom" :style="{ height: '70%' }" round>
      <div class="popup-content">
        <h3>我的发布</h3>
        <div v-if="myPosts.length > 0" class="my-posts-list">
          <div
            v-for="p in myPosts"
            :key="p.id"
            class="my-post-item"
            @click="goPost(p.id)"
          >
            <p>{{ p.content_preview || p.content }}</p>
            <span class="tag-capsule">{{ p.tag }}</span>
          </div>
        </div>
        <div v-else class="empty">还没有发布过内容</div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { postsApi } from '../api/posts'

const router = useRouter()
const authStore = useAuthStore()
const showMyPosts = ref(false)
const myPosts = ref<any[]>([])

const avatarColor = computed(() => {
  const seed = authStore.identity?.avatar_seed || '777777'
  return `#${seed.substring(0, 6)}`
})

const avatarText = computed(() => {
  const nick = authStore.identity?.nickname || '?'
  return nick.charAt(2) || nick.charAt(0)
})

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function goPost(id: number) {
  showMyPosts.value = false
  router.push(`/post/${id}`)
}

onMounted(async () => {
  if (!authStore.userInfo) {
    await authStore.fetchMe()
  }
  // Load user's posts
  try {
    const res = await postsApi.getList({})
    // Filter client-side for now (MVP simple approach)
    myPosts.value = (res.data.results || []).filter(
      (p: any) => p.is_author
    )
  } catch { /* ignore */ }
})
</script>

<style scoped>
.profile-page {
  max-width: 600px;
  margin: 0 auto;
}

.profile-header {
  text-align: center;
  padding: var(--space-8) 0;
  background: var(--brand-primary-light);
  border-radius: var(--card-radius);
  margin-bottom: var(--space-5);
}

.avatar-lg {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  margin: 0 auto var(--space-3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  font-weight: 700;
}

.profile-header h2 {
  font-size: 20px;
  margin-bottom: var(--space-1);
}

.join-date {
  font-size: 13px;
  color: var(--text-secondary);
}

.menu-card {
  background: var(--card-bg);
  border-radius: 20px;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  cursor: pointer;
  border-bottom: 1px solid var(--divider);
  font-size: 15px;
}

.menu-item:last-child {
  border-bottom: none;
}

.arrow {
  color: var(--text-secondary);
  font-size: 20px;
}

.popup-content {
  padding: var(--space-5);
}

.popup-content h3 {
  font-size: 18px;
  margin-bottom: var(--space-4);
}

.my-post-item {
  padding: var(--space-3);
  border-bottom: 1px solid var(--divider);
  cursor: pointer;
}

.my-post-item p {
  font-size: 14px;
  line-height: 22px;
  margin-bottom: var(--space-2);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tag-capsule {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.06);
}

.empty {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--space-8) 0;
}
</style>
