<template>
  <div class="profile-page">
    <section class="hero">
      <div class="hero-avatar-ring">
        <div class="hero-avatar">{{ avatarText }}</div>
      </div>
      <h1 class="hero-name">{{ authStore.identity?.nickname || '匿名旅人' }}</h1>
      <p class="hero-email">{{ maskedEmail }}</p>
      <p class="hero-join">加入于 {{ joinDate }}</p>

      <div class="hero-stats">
        <span><span class="num">{{ dashboard.stats.post_count }}</span> 发布</span>
        <span class="divider">·</span>
        <span><span class="num">{{ dashboard.stats.comment_count }}</span> 评论</span>
        <span class="divider">·</span>
        <span><span class="num">{{ dashboard.stats.favorite_count }}</span> 收藏</span>
      </div>

      <button class="hero-edit-btn" type="button" @click="activeTab = 'settings'">编辑设置</button>
    </section>

    <div class="tab-bar-wrap">
      <div class="tab-bar">
        <button class="tab-item" :class="{ active: activeTab === 'posts' }" type="button" @click="activeTab = 'posts'">我的发布</button>
        <button class="tab-item" :class="{ active: activeTab === 'comments' }" type="button" @click="activeTab = 'comments'">我的评论</button>
        <button class="tab-item" :class="{ active: activeTab === 'favorites' }" type="button" @click="activeTab = 'favorites'">我的收藏</button>
        <button class="tab-item" :class="{ active: activeTab === 'settings' }" type="button" @click="activeTab = 'settings'">设置</button>
      </div>
    </div>

    <section class="tab-content">
      <div v-if="activeTab === 'posts'" class="bento">
        <article class="bento-card card-posts">
          <div class="bento-header">
            <div class="bento-title"><span class="icon">🫧</span> 最近发布</div>
          </div>
          <div v-if="dashboard.posts.length" class="mini-posts">
            <div
              v-for="post in dashboard.posts"
              :key="post.id"
              class="mini-post"
              :class="[`b${post.bg_color}`, { disabled: !canOpenPost(post) }]"
              @click="openPost(post)"
            >
              <button class="action-btn delete" type="button" @click.stop="deletePost(post.id)">删除</button>
              <div class="mini-post-header">
                <div class="mini-post-avatar">{{ avatarText }}</div>
                <div class="mini-post-name">{{ authStore.identity?.nickname }}</div>
                <div class="mini-post-time">{{ formatTimeAgo(post.created_at) }}</div>
              </div>
              <div v-if="post.moderation_label" class="post-status" :class="post.status">{{ post.moderation_label }}</div>
              <div class="mini-post-body">{{ post.content_preview }}</div>
              <div class="mini-post-footer">
                <span>❤️ {{ post.like_count }}</span>
                <span>💬 {{ post.comment_count }}</span>
                <span>⭐ {{ post.favorite_count }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-card">还没有发布过内容</div>
        </article>

        <article class="bento-card card-stats">
          <div class="bento-header">
            <div class="bento-title"><span class="icon">📊</span> 活跃概览</div>
          </div>
          <div class="stats-grid">
            <div class="stat-box">
              <div class="stat-number purple">{{ dashboard.stats.post_count }}</div>
              <div class="stat-label">发布数量</div>
            </div>
            <div class="stat-box">
              <div class="stat-number teal">{{ dashboard.stats.comment_count }}</div>
              <div class="stat-label">评论数量</div>
            </div>
            <div class="stat-box">
              <div class="stat-number rose">{{ dashboard.stats.favorite_count }}</div>
              <div class="stat-label">收藏数量</div>
            </div>
          </div>
        </article>
      </div>

      <div v-else-if="activeTab === 'comments'" class="bento">
        <article class="bento-card card-comments wide">
          <div class="bento-header">
            <div class="bento-title"><span class="icon">💬</span> 最近评论</div>
          </div>
          <div v-if="dashboard.comments.length" class="mini-comments">
            <div v-for="comment in dashboard.comments" :key="comment.id" class="mini-comment">
              <div v-if="comment.moderation_label" class="post-status" :class="comment.status">{{ comment.moderation_label }}</div>
              <div class="mini-comment-text">{{ comment.content }}</div>
              <div class="mini-comment-meta">
                <span>{{ formatTimeAgo(comment.created_at) }}</span>
                <router-link v-if="comment.status !== 'rejected'" class="mini-comment-link" :to="`/post/${comment.post}#comments`">查看原帖</router-link>
              </div>
            </div>
          </div>
          <div v-else class="empty-card">还没有评论记录</div>
        </article>
      </div>

      <div v-else-if="activeTab === 'favorites'" class="bento">
        <article class="bento-card card-bookmarks wide">
          <div class="bento-header">
            <div class="bento-title"><span class="icon">⭐</span> 我的收藏</div>
          </div>
          <div v-if="dashboard.favorites.length" class="bookmark-grid">
            <div v-for="post in dashboard.favorites" :key="post.id" class="bookmark-mini" :class="`b${post.bg_color}`" @click="router.push(`/post/${post.id}`)">
              <button class="action-btn unbookmark" type="button" @click.stop="toggleFavorite(post.id)">取消收藏</button>
              <div class="bookmark-mini-body">{{ post.content_preview }}</div>
              <div class="bookmark-mini-footer">
                <span>❤️ {{ post.like_count }}</span>
                <span>💬 {{ post.comment_count }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-card">还没有收藏任何内容</div>
        </article>
      </div>

      <div v-else class="bento">
        <article class="bento-card card-settings wide">
          <div class="bento-header">
            <div class="bento-title"><span class="icon">⚙️</span> 账号设置</div>
          </div>
          <div class="settings-grid">
            <div class="setting-row">
              <div>
                <div class="setting-label">实名信息</div>
                <div class="setting-desc">这些信息用于后台审核，不会在前台公开显示。</div>
              </div>
            </div>

            <div class="setting-row stacked">
              <div class="setting-form-grid">
                <label class="setting-field">
                  <span>真实姓名</span>
                  <input v-model="realName" class="setting-input" type="text" placeholder="请输入真实姓名" />
                </label>
                <label class="setting-field">
                  <span>学号/工号</span>
                  <input v-model="studentId" class="setting-input" type="text" placeholder="请输入学号/工号" />
                </label>
              </div>
              <button class="logout-btn" type="button" @click="saveProfileInfo">保存实名信息</button>
            </div>

            <div class="setting-row">
              <div>
                <div class="setting-label">主题模式</div>
                <div class="setting-desc">跟随系统、深色、浅色模式会保存在本地和账号偏好里。</div>
              </div>
              <select class="setting-select" :value="themePreference" @change="setTheme(($event.target as HTMLSelectElement).value as any)">
                <option value="system">跟随系统</option>
                <option value="dark">深色模式</option>
                <option value="light">浅色模式</option>
              </select>
            </div>

            <div class="setting-row">
              <div>
                <div class="setting-label">当前邮箱</div>
                <div class="setting-desc">{{ authStore.userInfo?.email }}</div>
              </div>
            </div>

            <div class="setting-row">
              <div>
                <div class="setting-label">退出登录</div>
                <div class="setting-desc">离开当前设备的登录状态。</div>
              </div>
              <button class="logout-btn" type="button" @click="logout">退出登录</button>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api/auth'
import { postsApi } from '../api/posts'
import { useTheme } from '../composables/useTheme'
import { useAuthStore } from '../stores/auth'
import { formatTimeAgo, getIdentityInitial } from '../utils/presentation'

const router = useRouter()
const authStore = useAuthStore()
const { themePreference, setTheme } = useTheme()

const activeTab = ref<'posts' | 'comments' | 'favorites' | 'settings'>('posts')
const realName = ref('')
const studentId = ref('')
const dashboard = reactive<{
  posts: any[]
  comments: any[]
  favorites: any[]
  stats: { post_count: number; comment_count: number; favorite_count: number }
}>({
  posts: [],
  comments: [],
  favorites: [],
  stats: { post_count: 0, comment_count: 0, favorite_count: 0 },
})

const avatarText = computed(() => getIdentityInitial(authStore.identity?.nickname || '星'))
const maskedEmail = computed(() => {
  const email = authStore.userInfo?.email || ''
  const [name, domain] = email.split('@')
  if (!name || !domain) return email
  return `${name.slice(0, 2)}***@${domain}`
})
const joinDate = computed(() => {
  if (!authStore.userInfo?.date_joined) return ''
  return new Date(authStore.userInfo.date_joined).toLocaleDateString('zh-CN')
})

async function loadDashboard() {
  const res = await authApi.getDashboard()
  Object.assign(dashboard, res.data.data)
}

async function deletePost(id: number) {
  await postsApi.delete(id)
  await loadDashboard()
}

async function toggleFavorite(id: number) {
  await postsApi.toggleFavorite(id)
  await loadDashboard()
}

async function saveProfileInfo() {
  await authStore.updatePreferences({
    real_name: realName.value.trim(),
    student_id: studentId.value.trim(),
  })
}

function logout() {
  authStore.logout()
  router.push('/login')
}

function canOpenPost(post: any) {
  return post.status !== 'rejected'
}

function openPost(post: any) {
  if (!canOpenPost(post)) return
  router.push(`/post/${post.id}`)
}

onMounted(async () => {
  if (!authStore.userInfo) await authStore.fetchMe()
  realName.value = authStore.userInfo?.real_name || ''
  studentId.value = authStore.userInfo?.student_id || ''
  await loadDashboard()
})
</script>

<style scoped>
.profile-page {
  max-width: 1100px;
  margin: 0 auto;
}

.hero {
  padding: 48px 24px 32px;
  text-align: center;
}

.hero-avatar-ring {
  width: 104px;
  height: 104px;
  padding: 4px;
  margin: 0 auto 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--pink), var(--cyan));
}

.hero-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: var(--bg);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-1);
  font-size: 1.6rem;
  font-weight: 700;
}

.hero-name {
  margin: 0 0 6px;
  font-size: 1.5rem;
}

.hero-email,
.hero-join {
  margin: 0;
  color: var(--text-3);
}

.hero-join {
  margin-top: 4px;
  margin-bottom: 20px;
  font-size: 0.8125rem;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
  color: var(--text-2);
}

.hero-stats .num {
  color: var(--text-1);
  font-weight: 700;
}

.divider {
  color: var(--text-3);
}

.hero-edit-btn {
  min-height: 38px;
  padding: 0 24px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-1);
}

.hero-edit-btn:hover {
  color: var(--brand);
  border-color: var(--brand);
  background: rgba(124, 92, 252, 0.08);
}

.tab-bar-wrap {
  position: sticky;
  top: 64px;
  z-index: 10;
  padding: 12px 0;
  background: rgba(11, 13, 26, 0.6);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(16px);
}

.tab-bar {
  display: flex;
  width: fit-content;
  margin: 0 auto;
  gap: 6px;
  padding: 4px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border);
}

.tab-item {
  min-height: 42px;
  padding: 0 24px;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--text-2);
}

.tab-item.active {
  background: var(--brand);
  color: #fff;
  box-shadow: 0 2px 12px rgba(124, 92, 252, 0.3);
}

.tab-content {
  padding: 28px 16px 60px;
}

.bento {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.bento-card {
  position: relative;
  overflow: hidden;
  padding: 24px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
}

.card-posts,
.card-stats {
  grid-column: span 2;
}

.wide {
  grid-column: span 4;
}

.bento-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.bento-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 700;
}

.mini-posts,
.mini-comments {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mini-post,
.mini-comment,
.bookmark-mini,
.stat-box {
  position: relative;
  border-radius: 16px;
  border: 1px solid var(--border);
}

.mini-post {
  padding: 16px;
  cursor: pointer;
}

.mini-post.disabled {
  cursor: default;
}

.post-status {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 14px;
  font-size: 0.75rem;
  line-height: 1.5;
}

.post-status.rejected {
  background: rgba(255, 107, 107, 0.14);
  border: 1px solid rgba(255, 107, 107, 0.2);
  color: #ff8f8f;
}

.post-status.ai_suspect {
  background: rgba(255, 184, 108, 0.14);
  border: 1px solid rgba(255, 184, 108, 0.2);
  color: #ffc66d;
}

.mini-post-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.mini-post-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--gradient-brand);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.6875rem;
  font-weight: 700;
}

.mini-post-name {
  font-size: 0.75rem;
  font-weight: 600;
}

.mini-post-time {
  margin-left: auto;
  color: var(--text-3);
  font-size: 0.6875rem;
}

.mini-post-body,
.mini-comment-text,
.bookmark-mini-body {
  color: var(--text-2);
  line-height: 1.6;
}

.mini-post-body {
  margin-bottom: 10px;
  font-size: 0.8125rem;
}

.mini-post-footer,
.bookmark-mini-footer,
.mini-comment-meta {
  display: flex;
  gap: 12px;
  color: var(--text-3);
  font-size: 0.6875rem;
}

.mini-comment {
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
}

.mini-comment-text {
  margin-bottom: 8px;
  font-size: 0.8125rem;
}

.mini-comment-link {
  color: var(--brand);
}

.bookmark-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.bookmark-mini {
  padding: 14px;
  cursor: pointer;
}

.bookmark-mini-body {
  margin-bottom: 8px;
  font-size: 0.75rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.stat-box {
  padding: 20px 12px;
  text-align: center;
  background: rgba(255, 255, 255, 0.03);
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
}

.stat-number.purple {
  color: var(--brand);
}

.stat-number.teal {
  color: var(--cyan);
}

.stat-number.rose {
  color: var(--pink);
}

.stat-label {
  margin-top: 4px;
  color: var(--text-3);
  font-size: 0.8125rem;
}

.settings-grid {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.setting-row.stacked {
  align-items: flex-end;
}

.setting-row:first-child {
  border-top: 0;
  padding-top: 0;
}

.setting-label {
  font-size: 0.9375rem;
  font-weight: 600;
}

.setting-desc {
  color: var(--text-3);
  font-size: 0.8125rem;
}

.setting-select {
  min-width: 140px;
  min-height: 40px;
  padding: 0 12px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-1);
}

.setting-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  width: 100%;
}

.setting-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--text-2);
  font-size: 0.8125rem;
}

.setting-input {
  min-height: 42px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-1);
}

.logout-btn {
  min-height: 38px;
  padding: 0 18px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(248, 113, 113, 0.2);
  background: rgba(248, 113, 113, 0.08);
  color: var(--color-error);
}

.empty-card {
  color: var(--text-3);
  font-size: 0.875rem;
}

.action-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  min-height: 28px;
  padding: 0 12px;
  border-radius: var(--radius-pill);
  border: 1px solid transparent;
  opacity: 0;
}

.mini-post:hover .action-btn,
.bookmark-mini:hover .action-btn {
  opacity: 1;
}

.action-btn.delete {
  background: rgba(255, 60, 60, 0.15);
  border-color: rgba(255, 60, 60, 0.2);
  color: #ff6b6b;
}

.action-btn.unbookmark {
  background: rgba(255, 165, 89, 0.15);
  border-color: rgba(255, 165, 89, 0.2);
  color: #ffa559;
}

.b1 { background: var(--bubble-1); border-color: var(--bubble-1-border); }
.b2 { background: var(--bubble-2); border-color: var(--bubble-2-border); }
.b3 { background: var(--bubble-3); border-color: var(--bubble-3-border); }
.b4 { background: var(--bubble-4); border-color: var(--bubble-4-border); }
.b5 { background: var(--bubble-5); border-color: var(--bubble-5-border); }
.b6 { background: var(--bubble-6); border-color: var(--bubble-6-border); }
.b7 { background: var(--bubble-7); border-color: var(--bubble-7-border); }
.b8 { background: var(--bubble-8); border-color: var(--bubble-8-border); }

@media (max-width: 900px) {
  .bento {
    grid-template-columns: 1fr;
  }

  .card-posts,
  .card-stats,
  .wide {
    grid-column: span 1;
  }

  .stats-grid,
  .bookmark-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .tab-bar {
    width: 100%;
    overflow-x: auto;
    justify-content: flex-start;
  }

  .setting-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
