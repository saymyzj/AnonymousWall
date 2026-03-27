<template>
  <div class="layout">
    <StarryBackground />

    <!-- Navbar -->
    <nav class="navbar">
      <!-- Left: Logo -->
      <router-link to="/" class="logo">
        <span class="logo-icon">🫧</span>
        <span class="logo-text">AnonymousWall</span>
      </router-link>

      <!-- Center: Tabs / Search (scroll-linked) -->
      <div class="nav-center">
        <Transition name="fade" mode="out-in">
          <div v-if="showNavTabs" key="tabs" class="nav-tabs">
            <button
              v-for="tab in navTabItems"
              :key="tab.value"
              class="nav-tab"
              :class="{ active: activeNavTab === tab.value }"
              @click="switchNavTab(tab.value)"
            >
              {{ tab.label }}
            </button>
          </div>
          <div v-else key="search" class="nav-search">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              placeholder="搜索匿名心声..."
              @keyup.enter="doSearch"
            />
            <button v-if="searchQuery" class="search-clear" @click="clearSearch">×</button>
          </div>
        </Transition>
      </div>

      <!-- Right: User Area -->
      <div class="nav-right">
        <template v-if="authStore.isLoggedIn">
          <router-link to="/messages" class="nav-icon-btn" title="消息">
            🔔
            <span v-if="unreadCount" class="badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
          </router-link>
          <div class="user-menu" @mouseenter="showUserMenu = true" @mouseleave="showUserMenu = false">
            <div class="avatar-btn">
              {{ avatarEmoji }}
            </div>
            <Transition name="dropdown">
              <div v-if="showUserMenu" class="dropdown-menu">
                <router-link to="/profile" class="dropdown-item">
                  <span>👤</span> 个人中心
                </router-link>
                <router-link to="/messages" class="dropdown-item">
                  <span>✉️</span> 消息中心
                </router-link>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item logout" @click="handleLogout">
                  <span>🚪</span> 退出登录
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

    <!-- Content -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>

    <!-- FAB -->
    <button
      v-if="authStore.isLoggedIn && authStore.isVerified"
      class="fab"
      :class="{ hidden: !showFab }"
      @click="$router.push('/create')"
      title="发帖"
    >
      <span class="fab-icon">+</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { usePostsStore } from '../stores/posts'
import StarryBackground from '../components/StarryBackground.vue'

const router = useRouter()
const authStore = useAuthStore()
const postsStore = usePostsStore()

// Avatar
const avatarEmoji = computed(() => {
  const nick = authStore.identity?.nickname || '?'
  // Extract emoji-like character or first char
  return nick.charAt(0) === '匿' ? '🌟' : nick.charAt(0)
})

// Nav tabs
const navTabItems = [
  { label: '发现', value: 'latest' },
  { label: '热门', value: 'hot' },
  { label: '推荐', value: 'recommend' },
]
const activeNavTab = ref('latest')

function switchNavTab(value: string) {
  activeNavTab.value = value
  postsStore.setFilter('sort', value)
  router.push('/')
}

// Search scroll linkage
const showNavTabs = ref(true)
const searchQuery = ref('')
const unreadCount = ref(0) // TODO: fetch from API

function doSearch() {
  const q = searchQuery.value.trim()
  if (q) {
    postsStore.setFilter('search', q)
    router.push('/')
  }
}

function clearSearch() {
  searchQuery.value = ''
  postsStore.setFilter('search', undefined)
}

// IntersectionObserver for hero search visibility
let heroObserver: IntersectionObserver | null = null

function setupHeroObserver() {
  const heroSearch = document.getElementById('hero-search')
  if (!heroSearch) {
    showNavTabs.value = true
    return
  }
  heroObserver = new IntersectionObserver(
    ([entry]) => {
      showNavTabs.value = entry.isIntersecting
    },
    { threshold: 0 }
  )
  heroObserver.observe(heroSearch)
}

// User menu
const showUserMenu = ref(false)

function handleLogout() {
  showUserMenu.value = false
  authStore.logout()
  router.push('/login')
}

// FAB scroll hide/show
const showFab = ref(true)
let lastScrollY = 0

function onScroll() {
  const currentY = window.scrollY
  showFab.value = currentY < lastScrollY || currentY < 100
  lastScrollY = currentY
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  // Delay observer setup to wait for Home page render
  setTimeout(setupHeroObserver, 300)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  heroObserver?.disconnect()
})

// Re-setup observer on route change
router.afterEach(() => {
  heroObserver?.disconnect()
  setTimeout(setupHeroObserver, 300)
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
  position: relative;
}

/* ===== Navbar ===== */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  height: var(--nav-height);
  padding: 0 32px;
  background: var(--nav-bg);
  backdrop-filter: blur(24px) saturate(1.5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  gap: 24px;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.logo:hover { transform: scale(1.02); }
.logo-icon { font-size: 24px; }

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--brand), var(--pink));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Nav Center: Tabs / Search */
.nav-center {
  flex: 1;
  display: flex;
  justify-content: center;
  max-width: 400px;
  margin: 0 auto;
}

.nav-tabs {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-pill);
  padding: 4px;
}

.nav-tab {
  padding: 6px 20px;
  border-radius: var(--radius-pill);
  border: none;
  background: transparent;
  color: var(--text-2);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-tab:hover {
  color: var(--text-1);
  transform: none;
}

.nav-tab.active {
  background: var(--brand);
  color: #fff;
  transform: none;
}

/* Nav Search */
.nav-search {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  height: 38px;
  padding: 0 14px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-pill);
  transition: all 0.3s ease;
}

.nav-search:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 4px rgba(124, 92, 252, 0.25);
}

.search-icon { font-size: 14px; flex-shrink: 0; opacity: 0.5; }

.nav-search input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-1);
  outline: none;
}

.nav-search input::placeholder { color: var(--text-3); }

.search-clear {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-2);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.search-clear:hover { background: rgba(255, 255, 255, 0.2); transform: none; }

/* Fade transition for tabs/search switch */
.fade-enter-active,
.fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }

/* Nav Right */
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.nav-icon-btn {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  background: var(--pink);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.nav-btn {
  padding: 8px 20px;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-btn.ghost {
  color: var(--text-2);
}

.nav-btn.ghost:hover {
  color: var(--text-1);
  background: rgba(255, 255, 255, 0.06);
}

.nav-btn.primary {
  background: var(--brand);
  color: white;
}

.nav-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(124, 92, 252, 0.3);
  color: white;
}

/* User Menu */
.user-menu { position: relative; }

.avatar-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--pink));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.avatar-btn:hover {
  transform: scale(1.08);
  box-shadow: 0 0 0 3px rgba(124, 92, 252, 0.2);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 180px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  padding: 8px;
  z-index: 200;
  backdrop-filter: blur(20px);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-1);
  text-decoration: none;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  transition: background 0.15s ease;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--brand);
}

.dropdown-item.logout:hover {
  color: var(--color-error);
  background: rgba(248, 113, 113, 0.08);
}

.dropdown-divider {
  height: 1px;
  background: var(--divider);
  margin: 4px 8px;
}

.dropdown-enter-active { transition: all 0.2s ease; }
.dropdown-leave-active { transition: all 0.15s ease; }
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}

/* ===== Main Content ===== */
.main-content {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 48px;
  padding-top: calc(var(--nav-height) + 24px);
}

/* ===== FAB ===== */
.fab {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, var(--brand), var(--pink));
  color: white;
  font-size: 28px;
  cursor: pointer;
  box-shadow: 0 6px 32px rgba(124, 92, 252, 0.25);
  z-index: 99;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.fab-icon {
  display: block;
  transition: transform 0.3s ease;
  line-height: 1;
}

.fab:hover {
  transform: scale(1.1) translateY(-2px);
  box-shadow: 0 0 60px rgba(124, 92, 252, 0.25);
}

.fab:hover .fab-icon { transform: rotate(90deg); }
.fab:active { transform: scale(0.95); }

.fab.hidden {
  transform: translateY(100px);
  opacity: 0;
  pointer-events: none;
}

/* ===== Page Transition ===== */
.page-fade-enter-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.page-fade-leave-active { transition: opacity 0.15s ease; }
.page-fade-enter-from { opacity: 0; transform: translateY(8px); }
.page-fade-leave-to { opacity: 0; }

/* ===== Responsive ===== */
@media (max-width: 900px) {
  .navbar { padding: 0 24px; }
  .main-content { padding: 24px 24px; padding-top: calc(var(--nav-height) + 24px); }
}

@media (max-width: 600px) {
  .nav-center { display: none; }
  .main-content { padding: 16px; padding-top: calc(var(--nav-height) + 16px); }
  .nav-btn.ghost { display: none; }
}
</style>
