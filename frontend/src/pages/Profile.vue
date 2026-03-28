<template>
  <div class="profile-page">
    <section class="hero">
      <div class="hero-shell">
        <div class="hero-rings">
          <div class="hero-avatar">{{ avatarText }}</div>
        </div>
        <div class="hero-kicker">匿名星球成员</div>
        <h1 class="hero-name">{{ authStore.identity?.nickname || '匿名旅人' }}</h1>
        <p class="hero-email">{{ maskedEmail }}</p>
        <p class="hero-join">加入于 {{ joinDate }}</p>

        <div class="hero-stats">
          <div class="hero-stat">
            <strong>{{ dashboard.stats.post_count }}</strong>
            <span>累计发布</span>
          </div>
          <div class="hero-stat">
            <strong>{{ dashboard.stats.comment_count }}</strong>
            <span>评论互动</span>
          </div>
          <div class="hero-stat">
            <strong>{{ dashboard.stats.favorite_count }}</strong>
            <span>我的收藏</span>
          </div>
        </div>

        <div class="hero-actions">
          <button class="primary-btn" type="button" @click="scrollToSettings">编辑设置</button>
          <button class="ghost-btn" type="button" @click="refreshIdentity">刷新身份</button>
        </div>
      </div>
    </section>

    <main class="dashboard-wrap">
      <div class="dashboard">
        <!-- Posts Panel -->
        <section class="panel panel-posts">
          <div class="panel-header">
            <div class="panel-title"><span class="icon">🫧</span> 最近发布</div>
          </div>
          <div v-if="dashboard.posts.length" class="post-list stagger-fade-in">
            <div
              v-for="post in dashboard.posts"
              :key="post.id"
              class="post-card"
              :class="[`b${post.bg_color}`, { disabled: !canOpenPost(post) }]"
              @click="openPost(post)"
            >
              <button class="card-action delete" type="button" @click.stop="deletePost(post.id)">删除</button>
              <div class="post-card-header">
                <div class="post-card-avatar">{{ avatarText }}</div>
                <div class="post-card-meta">
                  <div class="post-card-name">{{ authStore.identity?.nickname }}</div>
                  <div class="post-card-time">{{ formatTimeAgo(post.created_at) }}</div>
                </div>
              </div>
              <div v-if="post.moderation_label" class="moderation-badge" :class="post.status">{{ post.moderation_label }}</div>
              <div class="post-card-body">{{ post.content_preview }}</div>
              <div class="post-card-footer">
                <span>❤️ {{ post.like_count }}</span>
                <span>💬 {{ post.comment_count }}</span>
                <span>⭐ {{ post.favorite_count }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">🫧</div>
            <p>还没有发布过内容</p>
          </div>
        </section>

        <!-- Comments Panel -->
        <section class="panel panel-comments">
          <div class="panel-header">
            <div class="panel-title"><span class="icon">💬</span> 评论动态</div>
          </div>
          <div v-if="dashboard.comments.length" class="comment-list stagger-fade-in">
            <div v-for="comment in dashboard.comments" :key="comment.id" class="comment-card">
              <div v-if="comment.moderation_label" class="moderation-badge" :class="comment.status">{{ comment.moderation_label }}</div>
              <div class="comment-card-text">{{ comment.content }}</div>
              <div class="comment-card-meta">
                <span>{{ formatTimeAgo(comment.created_at) }}</span>
                <router-link v-if="comment.status !== 'rejected'" class="comment-card-link" :to="`/post/${comment.post}#comments`">查看原帖 →</router-link>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">💬</div>
            <p>还没有评论记录</p>
          </div>
        </section>

        <!-- Favorites Panel -->
        <section class="panel panel-favorites">
          <div class="panel-header">
            <div class="panel-title"><span class="icon">⭐</span> 收藏夹</div>
          </div>
          <div v-if="dashboard.favorites.length" class="bookmark-grid stagger-fade-in">
            <div v-for="post in dashboard.favorites" :key="post.id" class="bookmark-card" :class="`b${post.bg_color}`" @click="router.push(`/post/${post.id}`)">
              <button class="card-action unbookmark" type="button" @click.stop="toggleFavorite(post.id)">取消收藏</button>
              <div class="bookmark-card-body">{{ post.content_preview }}</div>
              <div class="bookmark-card-footer">
                <span>❤️ {{ post.like_count }}</span>
                <span>💬 {{ post.comment_count }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">⭐</div>
            <p>还没有收藏任何内容</p>
          </div>
        </section>
      </div>

      <!-- Settings Panel (full width, below the bento grid) -->
      <section ref="settingsRef" class="panel panel-settings">
        <div class="panel-header">
          <div class="panel-title"><span class="icon">⚙️</span> 账号设置</div>
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
            <div class="setting-action-row">
              <button class="save-btn" type="button" @click="saveProfileInfo">保存实名信息</button>
            </div>
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
      </section>
    </main>
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

const settingsRef = ref<HTMLElement>()
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

function scrollToSettings() {
  settingsRef.value?.scrollIntoView({ behavior: 'smooth' })
}

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

async function refreshIdentity() {
  await authStore.refreshIdentity()
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

/* ===== HERO ===== */
.hero {
  position: relative;
  padding: 48px 24px 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-shell {
  width: min(860px, 100%);
  text-align: center;
}

.hero-rings {
  width: 132px;
  height: 132px;
  padding: 5px;
  margin: 0 auto 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--cyan), var(--brand), var(--pink));
  box-shadow: 0 0 40px var(--glow-brand);
  animation: nebula-pulse 6s ease-in-out infinite;
}

.hero-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-1);
  font-size: 2.4rem;
  font-weight: 700;
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  margin-bottom: 18px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(124, 92, 252, 0.25);
  background: rgba(124, 92, 252, 0.1);
  color: var(--brand);
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.hero-name {
  margin: 0 0 14px;
  font-size: clamp(1.8rem, 5vw, 2.8rem);
  font-weight: 800;
  line-height: 1.04;
}

.hero-email {
  margin: 0;
  color: var(--text-2);
  font-size: 1.0625rem;
}

.hero-join {
  margin: 4px 0 28px;
  color: var(--text-3);
  font-size: 0.9375rem;
}

.hero-stats {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 26px;
}

.hero-stat {
  min-width: 142px;
  padding: 16px 18px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  text-align: center;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.hero-stat:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px var(--glow-brand);
}

.hero-stat strong {
  display: block;
  font-size: 1.75rem;
  margin-bottom: 4px;
  color: var(--text-1);
}

.hero-stat span {
  color: var(--text-3);
  font-size: 0.8125rem;
}

.hero-actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
}

.primary-btn,
.ghost-btn {
  padding: 13px 26px;
  border-radius: var(--radius-pill);
  border: 1px solid transparent;
  font-weight: 700;
  font-size: 0.875rem;
}

.primary-btn {
  color: #fff;
  background: var(--gradient-brand);
  box-shadow: 0 12px 30px var(--glow-brand);
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 36px var(--glow-brand);
}

.ghost-btn {
  color: var(--text-1);
  background: var(--glass-bg);
  border-color: var(--border);
}

.ghost-btn:hover {
  border-color: var(--brand);
  color: var(--brand);
}

/* ===== BENTO DASHBOARD ===== */
.dashboard-wrap {
  position: relative;
  margin-top: -80px;
}

.dashboard {
  display: grid;
  grid-template-columns: 1.8fr 1fr 1fr;
  gap: 18px;
}

.panel {
  padding: 24px;
  border-radius: 28px;
  background: var(--glass-bg);
  border: 1px solid var(--border);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow-soft);
}

.panel-settings {
  margin-top: 18px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 800;
}

/* ===== POST CARDS ===== */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.post-card {
  position: relative;
  padding: 20px;
  border-radius: 22px;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 40px var(--glow-brand);
}

.post-card.disabled {
  cursor: default;
  opacity: 0.6;
}

.post-card.disabled:hover {
  transform: none;
  box-shadow: none;
}

.card-action {
  position: absolute;
  top: 14px;
  right: 14px;
  min-height: 28px;
  padding: 0 12px;
  border-radius: var(--radius-pill);
  border: 1px solid transparent;
  font-size: 0.75rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.post-card:hover .card-action,
.bookmark-card:hover .card-action {
  opacity: 1;
}

.card-action.delete {
  background: rgba(255, 60, 60, 0.15);
  border-color: rgba(255, 60, 60, 0.2);
  color: #ff6b6b;
}

.card-action.unbookmark {
  background: rgba(255, 165, 89, 0.15);
  border-color: rgba(255, 165, 89, 0.2);
  color: #ffa559;
}

.moderation-badge {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 14px;
  font-size: 0.75rem;
  line-height: 1.5;
}

.moderation-badge.rejected {
  background: rgba(255, 107, 107, 0.14);
  border: 1px solid rgba(255, 107, 107, 0.2);
  color: #ff8f8f;
}

.moderation-badge.ai_suspect {
  background: rgba(255, 184, 108, 0.14);
  border: 1px solid rgba(255, 184, 108, 0.2);
  color: #ffc66d;
}

.post-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.post-card-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--gradient-brand);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
}

.post-card-meta {
  flex: 1;
}

.post-card-name {
  font-size: 0.8125rem;
  font-weight: 600;
}

.post-card-time {
  color: var(--text-3);
  font-size: 0.6875rem;
}

.post-card-body {
  color: var(--text-2);
  font-size: 0.875rem;
  line-height: 1.6;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-card-footer {
  display: flex;
  gap: 14px;
  color: var(--text-3);
  font-size: 0.75rem;
}

/* ===== COMMENTS ===== */
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.comment-card {
  padding: 18px;
  border-radius: 22px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.comment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px var(--glow-brand);
}

.comment-card-text {
  color: var(--text-1);
  font-size: 0.9375rem;
  line-height: 1.7;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.comment-card-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--text-3);
  font-size: 0.8125rem;
}

.comment-card-link {
  color: var(--brand);
}

.comment-card-link:hover {
  color: var(--pink);
}

/* ===== BOOKMARKS ===== */
.bookmark-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.bookmark-card {
  position: relative;
  min-height: 160px;
  padding: 18px;
  border-radius: 22px;
  border: 1px solid var(--border);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.bookmark-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px var(--glow-brand);
}

.bookmark-card-body {
  color: var(--text-2);
  font-size: 0.875rem;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bookmark-card-footer {
  display: flex;
  gap: 14px;
  color: var(--text-3);
  font-size: 0.75rem;
  margin-top: 12px;
}

/* ===== SETTINGS ===== */
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
  border-top: 1px solid var(--divider);
}

.setting-row.stacked {
  flex-direction: column;
  align-items: stretch;
  gap: 16px;
}

.setting-action-row {
  display: flex;
  justify-content: flex-end;
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
  background: var(--bg-card);
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
  background: var(--bg-card);
  color: var(--text-1);
}

.setting-input:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--glow-brand);
}

.save-btn {
  min-height: 38px;
  padding: 0 18px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(6, 214, 160, 0.2);
  background: rgba(6, 214, 160, 0.08);
  color: var(--cyan);
}

.save-btn:hover {
  background: rgba(6, 214, 160, 0.15);
}

.logout-btn {
  min-height: 38px;
  padding: 0 18px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(248, 113, 113, 0.2);
  background: rgba(248, 113, 113, 0.08);
  color: var(--color-error);
}

.logout-btn:hover {
  background: rgba(248, 113, 113, 0.15);
}

/* ===== EMPTY STATE ===== */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-3);
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* ===== BUBBLE COLORS ===== */
.b1 { background: var(--bubble-1); border-color: var(--bubble-1-border); }
.b2 { background: var(--bubble-2); border-color: var(--bubble-2-border); }
.b3 { background: var(--bubble-3); border-color: var(--bubble-3-border); }
.b4 { background: var(--bubble-4); border-color: var(--bubble-4-border); }
.b5 { background: var(--bubble-5); border-color: var(--bubble-5-border); }
.b6 { background: var(--bubble-6); border-color: var(--bubble-6-border); }
.b7 { background: var(--bubble-7); border-color: var(--bubble-7-border); }
.b8 { background: var(--bubble-8); border-color: var(--bubble-8-border); }

/* ===== RESPONSIVE ===== */
@media (max-width: 1180px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .hero {
    padding: 36px 18px 100px;
  }

  .dashboard-wrap {
    margin-top: -60px;
  }

  .panel {
    padding: 18px;
    border-radius: 24px;
  }

  .bookmark-grid {
    grid-template-columns: 1fr;
  }

  .hero-stat {
    min-width: calc(50% - 8px);
  }

  .setting-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
