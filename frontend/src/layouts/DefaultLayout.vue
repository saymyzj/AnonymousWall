<template>
  <div class="layout">
    <StarryBackground />
    <ToastContainer />

    <nav class="navbar">
      <div class="nav-left">
        <router-link to="/" class="logo" aria-label="返回首页">
          <span class="logo-icon">🫧</span>
          <span class="logo-text">匿名宇宙</span>
        </router-link>
      </div>

      <div v-if="showCenterSlot" class="nav-center">
        <Transition name="fade" mode="out-in">
          <div v-if="showNavTabs" key="tabs" class="nav-tabs">
            <button
              v-for="tab in navTabItems"
              :key="tab.value"
              class="nav-tab"
              :class="{ active: activeNavTab === tab.value }"
              type="button"
              @click="switchNavTab(tab.value)"
            >
              {{ tab.label }}
            </button>
          </div>

          <form v-else key="search" class="nav-search" @submit.prevent="submitSearch">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              type="search"
              placeholder="搜索匿名心声..."
              aria-label="搜索匿名心声"
            />
            <button v-if="searchQuery" class="search-clear" type="button" @click="clearSearch">
              ×
            </button>
          </form>
        </Transition>
      </div>

      <div class="nav-right">
        <button
          v-if="authStore.isLoggedIn"
          class="icon-shell"
          type="button"
          title="通知中心"
          @click="router.push('/messages?tab=notifications')"
        >
          🔔
          <span v-if="unreadNotifications" class="dot"></span>
        </button>

        <button
          v-if="authStore.isLoggedIn"
          class="icon-shell"
          type="button"
          title="消息中心"
          @click="router.push('/messages?tab=messages')"
        >
          ✉️
          <span v-if="unreadMessages" class="dot secondary"></span>
        </button>

        <button
          class="icon-shell"
          type="button"
          :title="`切换主题模式，当前：${themeTitle}`"
          @click="cycleTheme"
        >
          {{ themeIcon }}
        </button>

        <template v-if="authStore.isLoggedIn">
          <div class="user-menu" @mouseenter="showUserMenu = true" @mouseleave="showUserMenu = false">
            <button class="avatar-btn" type="button" aria-label="打开用户菜单">
              {{ avatarEmoji }}
            </button>

            <Transition name="dropdown">
              <div v-if="showUserMenu" class="dropdown-menu">
                <router-link to="/profile" class="dropdown-item">
                  <span>👤</span>
                  <span>个人中心</span>
                </router-link>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item logout" type="button" @click="handleLogout">
                  <span>🚪</span>
                  <span>退出登录</span>
                </button>
              </div>
            </Transition>
          </div>
        </template>

        <template v-else>
          <router-link to="/login" class="nav-btn ghost">登录</router-link>
          <router-link to="/login?mode=register" class="nav-btn primary">注册</router-link>
        </template>
      </div>
    </nav>

    <main class="main-content" :class="{ compact: isDetailRoute }">
      <router-view v-slot="{ Component }">
        <Transition name="page-slide" appear>
          <component :is="Component" :key="route.path" />
        </Transition>
      </router-view>
    </main>

    <button
      v-if="showFabButton"
      class="fab"
      :class="{ hidden: !showFab }"
      type="button"
      title="发布一个新气泡"
      @click="router.push('/create')"
    >
      <span class="fab-icon">+</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { messagesApi } from '../api/messages'
import StarryBackground from '../components/StarryBackground.vue'
import ToastContainer from '../components/ToastContainer.vue'
import { useTheme } from '../composables/useTheme'
import { useAuthStore } from '../stores/auth'
import { usePostsStore } from '../stores/posts'
import { getIdentityInitial } from '../utils/presentation'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const postsStore = usePostsStore()
const { themePreference, cycleTheme } = useTheme()

const navTabItems = [
  { label: '发现', value: 'latest' },
  { label: '热门', value: 'hot' },
  { label: '推荐', value: 'recommend' },
]

const showUserMenu = ref(false)
const showNavTabs = ref(true)
const searchQuery = ref('')
const showFab = ref(true)
const unreadNotifications = ref(0)
const unreadMessages = ref(0)

const isHomeRoute = computed(() => route.name === 'Home')
const isDetailRoute = computed(() => route.name === 'PostDetail')
const showCenterSlot = computed(() => isHomeRoute.value)
const activeNavTab = computed(() => postsStore.filters.sort || 'latest')
const avatarEmoji = computed(() => getIdentityInitial(authStore.identity?.nickname || '星'))
const themeIcon = computed(() => {
  if (themePreference.value === 'light') return '☀️'
  if (themePreference.value === 'dark') return '🌙'
  return '🖥️'
})
const themeTitle = computed(() => {
  if (themePreference.value === 'light') return '浅色模式'
  if (themePreference.value === 'dark') return '深色模式'
  return '跟随系统'
})
const showFabButton = computed(
  () =>
    authStore.isLoggedIn &&
    authStore.isVerified &&
    isHomeRoute.value,
)

let heroObserver: IntersectionObserver | null = null
let lastScrollY = 0

function cleanupHeroObserver() {
  heroObserver?.disconnect()
  heroObserver = null
}

async function setupHeroObserver() {
  cleanupHeroObserver()
  if (!isHomeRoute.value) {
    showNavTabs.value = false
    return
  }

  await nextTick()
  const heroSearch = document.getElementById('hero-search')
  if (!heroSearch) {
    showNavTabs.value = true
    return
  }

  heroObserver = new IntersectionObserver(
    ([entry]) => {
      showNavTabs.value = entry.isIntersecting
    },
    {
      rootMargin: '-72px 0px 0px 0px',
      threshold: 0.12,
    },
  )
  heroObserver.observe(heroSearch)
}

function switchNavTab(value: string) {
  if (route.name !== 'Home') {
    router.push({ name: 'Home' })
  }
  postsStore.setFilter('sort', value)
}

function submitSearch() {
  const query = searchQuery.value.trim()
  if (route.name !== 'Home') {
    router.push({ name: 'Home' })
  }
  postsStore.setFilter('search', query || undefined)
}

function clearSearch() {
  searchQuery.value = ''
  postsStore.setFilter('search', undefined)
}

function handleLogout() {
  showUserMenu.value = false
  authStore.logout()
  router.push('/login')
}

function onScroll() {
  const currentY = window.scrollY
  showFab.value = currentY < lastScrollY || currentY < 120
  lastScrollY = currentY
}

async function loadUnreadCounts() {
  if (!authStore.isLoggedIn) {
    unreadNotifications.value = 0
    unreadMessages.value = 0
    return
  }
  try {
    const res = await messagesApi.getUnreadSummary()
    unreadMessages.value = res.data.data.messages || 0
    unreadNotifications.value = res.data.data.notifications || 0
  } catch {
    unreadNotifications.value = 0
    unreadMessages.value = 0
  }
}

watch(
  () => route.fullPath,
  async () => {
    searchQuery.value = postsStore.filters.search || ''
    await loadUnreadCounts()
    await setupHeroObserver()
  },
  { immediate: true },
)

watch(
  () => postsStore.filters.search,
  (value) => {
    searchQuery.value = value || ''
  },
  { immediate: true },
)

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  loadUnreadCounts()
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  cleanupHeroObserver()
})
</script>

<style scoped>
.layout {
  position: relative;
  min-height: 100vh;
}

.navbar {
  position: fixed;
  inset: 0 0 auto;
  z-index: 100;
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto minmax(220px, 1fr);
  align-items: center;
  gap: 24px;
  height: var(--nav-height);
  padding: 0 36px;
  background: var(--nav-bg);
  border-bottom: 1px solid var(--border-soft);
  backdrop-filter: blur(24px) saturate(1.5);
  -webkit-backdrop-filter: blur(24px) saturate(1.5);
}

.nav-left,
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-right {
  justify-content: flex-end;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 1.4rem;
}

.logo-text {
  font-size: 1.125rem;
  font-weight: 700;
  background: var(--gradient-brand);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.nav-center {
  min-width: 300px;
  display: flex;
  justify-content: center;
}

.nav-tabs {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: var(--radius-pill);
  background: var(--bg-card);
  border: 1px solid var(--border-soft);
}

.nav-tab {
  min-width: 72px;
  padding: 8px 18px;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--text-2);
  font-size: 0.875rem;
  font-weight: 500;
}

.nav-tab:hover {
  color: var(--text-1);
}

.nav-tab.active {
  color: #fff;
  background: var(--brand);
  box-shadow: 0 10px 20px rgba(124, 92, 252, 0.18);
}

.nav-search {
  width: min(420px, 100%);
  display: flex;
  align-items: center;
  gap: 10px;
  height: 40px;
  padding: 0 14px;
  border-radius: var(--radius-pill);
  background: var(--bg-card);
  border: 1px solid var(--border);
}

.nav-search:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 4px rgba(124, 92, 252, 0.25);
}

.search-icon {
  font-size: 0.875rem;
  opacity: 0.7;
}

.nav-search input {
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text-1);
}

.nav-search input::placeholder {
  color: var(--text-3);
}

.search-clear,
.icon-shell,
.avatar-btn {
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-2);
}

.search-clear,
.icon-shell {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.search-clear {
  width: 24px;
  height: 24px;
  border: 0;
  background: var(--bg-card-hover);
}

.search-clear:hover,
.icon-shell:hover {
  color: var(--text-1);
  border-color: var(--border-hover);
  background: var(--bg-card-hover);
}

.icon-shell {
  position: relative;
}

.dot {
  position: absolute;
  top: 7px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--pink);
  box-shadow: 0 0 0 4px rgba(255, 107, 157, 0.12);
}

.dot.secondary {
  background: var(--cyan);
  box-shadow: 0 0 0 4px rgba(6, 214, 160, 0.12);
}

.avatar-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--gradient-brand);
  color: #fff;
  font-weight: 600;
}

.avatar-btn:hover {
  transform: scale(1.06);
  box-shadow: 0 0 0 4px rgba(124, 92, 252, 0.16);
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 18px;
  border-radius: var(--radius-pill);
  font-size: 0.875rem;
  font-weight: 600;
}

.nav-btn.ghost {
  color: var(--text-2);
}

.nav-btn.ghost:hover {
  color: var(--text-1);
  background: var(--bg-card);
}

.nav-btn.primary {
  color: #fff;
  background: var(--gradient-brand);
  box-shadow: 0 8px 20px rgba(124, 92, 252, 0.18);
}

.nav-btn.primary:hover {
  transform: translateY(-1px);
}

.user-menu {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 180px;
  padding: 8px;
  border-radius: 18px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-floating);
  backdrop-filter: blur(24px);
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--text-1);
}

.dropdown-item:hover {
  color: var(--brand);
  background: var(--bg-card);
}

.dropdown-item.logout:hover {
  color: var(--color-error);
  background: rgba(248, 113, 113, 0.08);
}

.dropdown-divider {
  height: 1px;
  margin: 6px 8px;
  background: var(--divider);
}

.main-content {
  position: relative;
  z-index: 1;
  width: min(var(--page-max-width), 100%);
  margin: 0 auto;
  padding: calc(var(--nav-height) + 24px) 48px 64px;
}

.main-content.compact {
  width: min(1040px, 100%);
}

.fab {
  position: fixed;
  right: 32px;
  bottom: 32px;
  z-index: 99;
  width: 56px;
  height: 56px;
  border: 0;
  border-radius: 50%;
  background: var(--gradient-brand);
  color: #fff;
  box-shadow: 0 6px 32px rgba(124, 92, 252, 0.25);
}

.fab:hover {
  transform: scale(1.1) translateY(-2px);
  box-shadow: 0 0 60px rgba(124, 92, 252, 0.25);
}

.fab.hidden {
  opacity: 0;
  pointer-events: none;
  transform: translateY(96px);
}

.fab-icon {
  display: inline-block;
  font-size: 1.8rem;
  line-height: 1;
}

.fade-enter-active,
.fade-leave-active,
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.24s ease;
}

.fade-enter-from,
.fade-leave-to,
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
}

.dropdown-enter-from,
.dropdown-leave-to {
  transform: translateY(-8px) scale(0.96);
}

.page-slide-enter-active {
  transition: opacity 0.28s ease, transform 0.28s ease;
}

.page-slide-leave-active {
  transition: opacity 0.15s ease;
  position: absolute;
  width: 100%;
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.page-slide-leave-to {
  opacity: 0;
}

@media (max-width: 900px) {
  .navbar {
    grid-template-columns: auto 1fr auto;
    gap: 16px;
    padding: 0 22px;
  }

  .nav-center {
    min-width: 0;
  }

  .main-content {
    padding: calc(var(--nav-height) + 20px) 24px 56px;
  }
}

@media (max-width: 600px) {
  .navbar {
    padding: 0 16px;
    grid-template-columns: auto 1fr auto;
  }

  .nav-center {
    display: none;
  }

  .logo-text {
    font-size: 1rem;
  }

  .nav-btn.ghost {
    display: none;
  }

  .main-content {
    padding: calc(var(--nav-height) + 16px) 16px 48px;
  }

  .fab {
    right: 18px;
    bottom: 18px;
  }

}
</style>
