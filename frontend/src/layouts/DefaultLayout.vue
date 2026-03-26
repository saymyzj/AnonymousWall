<template>
  <div class="layout">
    <!-- Background Decorative Bubbles -->
    <div class="bg-bubbles" aria-hidden="true">
      <div class="bg-bubble b1"></div>
      <div class="bg-bubble b2"></div>
      <div class="bg-bubble b3"></div>
      <div class="bg-bubble b4"></div>
    </div>

    <!-- Navbar -->
    <nav class="navbar">
      <!-- Left: Logo -->
      <router-link to="/" class="logo">
        <span class="logo-icon">🫧</span>
        <span class="logo-text">AnonymousWall</span>
      </router-link>

      <!-- Center: Search Bar (always visible) -->
      <div class="search-bar" :class="{ focused: searchFocused }">
        <span class="search-icon">🔍</span>
        <input
          ref="searchInput"
          v-model="searchQuery"
          placeholder="搜索匿名心声..."
          @focus="searchFocused = true"
          @blur="searchFocused = false"
          @keyup.enter="doSearch"
        />
        <button v-if="searchQuery" class="search-clear" @click="clearSearch">×</button>
      </div>

      <!-- Right: User Area -->
      <div class="nav-right">
        <template v-if="authStore.isLoggedIn">
          <div class="user-menu" @mouseenter="showUserMenu = true" @mouseleave="showUserMenu = false">
            <div class="avatar-btn" :style="{ background: avatarColor }">
              {{ avatarText }}
            </div>
            <Transition name="dropdown">
              <div v-if="showUserMenu" class="dropdown-menu">
                <router-link to="/profile" class="dropdown-item">
                  <span>👤</span> 个人中心
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
          <router-link to="/login" class="nav-btn nav-btn-ghost">登录</router-link>
          <router-link to="/login" class="nav-btn nav-btn-primary">注册</router-link>
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

const router = useRouter()
const authStore = useAuthStore()
const postsStore = usePostsStore()

const avatarText = computed(() => {
  const nick = authStore.identity?.nickname || '?'
  return nick.charAt(2) || nick.charAt(0)
})

const avatarColor = computed(() => {
  const seed = authStore.identity?.avatar_seed || '000'
  return `#${seed.substring(0, 6)}`
})

// Search
const searchFocused = ref(false)
const searchQuery = ref('')
const searchInput = ref<HTMLInputElement>()

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
  searchInput.value?.focus()
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

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

/* ===== Navbar ===== */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  height: 72px;
  padding: 0 40px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--divider);
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

.logo:hover {
  transform: scale(1.02);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Search Bar — always visible in center */
.search-bar {
  flex: 1;
  max-width: 480px;
  height: 44px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 22px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.search-bar:hover {
  background: rgba(0, 0, 0, 0.06);
}

.search-bar.focused {
  background: white;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 4px rgba(124, 92, 252, 0.1);
}

.search-icon {
  font-size: 16px;
  flex-shrink: 0;
  opacity: 0.5;
}

.search-bar input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
}

.search-bar input::placeholder {
  color: var(--text-placeholder);
}

.search-clear {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.08);
  color: var(--text-secondary);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.search-clear:hover {
  background: rgba(0, 0, 0, 0.15);
  transform: none;
}

/* Nav Right */
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.nav-btn {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-btn-ghost {
  color: var(--text-primary);
}

.nav-btn-ghost:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--brand-primary);
}

.nav-btn-primary {
  background: var(--brand-primary);
  color: white;
}

.nav-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(124, 92, 252, 0.3);
  color: white;
}

/* User Menu Dropdown */
.user-menu {
  position: relative;
}

.avatar-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 15px;
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
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  padding: 8px;
  z-index: 200;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  text-decoration: none;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  transition: background 0.15s ease;
}

.dropdown-item:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--brand-primary);
}

.dropdown-item.logout:hover {
  color: var(--color-error);
  background: rgba(248, 113, 113, 0.06);
}

.dropdown-divider {
  height: 1px;
  background: var(--divider);
  margin: 4px 8px;
}

.dropdown-enter-active { transition: all 0.2s ease; }
.dropdown-leave-active { transition: all 0.15s ease; }
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}

/* ===== Main Content ===== */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 40px;
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
  background: linear-gradient(135deg, var(--brand-primary), #9B7BFC);
  color: white;
  font-size: 28px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(124, 92, 252, 0.3);
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
  transform: scale(1.1);
  box-shadow: 0 12px 36px rgba(124, 92, 252, 0.4);
}

.fab:hover .fab-icon {
  transform: rotate(90deg);
}

.fab:active {
  transform: scale(0.95);
}

.fab.hidden {
  transform: translateY(100px);
  opacity: 0;
  pointer-events: none;
}

/* ===== Background Bubbles ===== */
.bg-bubbles {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}

.bg-bubble {
  position: absolute;
  border-radius: 50%;
  opacity: 0.12;
  animation: bubble-drift 25s ease-in-out infinite;
}

.bg-bubble.b1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #7C5CFC, transparent 70%);
  top: -5%;
  left: -5%;
  animation-duration: 30s;
}

.bg-bubble.b2 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #FF6B9D, transparent 70%);
  top: 50%;
  right: -5%;
  animation-duration: 22s;
  animation-delay: -7s;
}

.bg-bubble.b3 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, #34D399, transparent 70%);
  bottom: -3%;
  left: 25%;
  animation-duration: 26s;
  animation-delay: -12s;
}

.bg-bubble.b4 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #60A5FA, transparent 70%);
  top: 20%;
  right: 30%;
  animation-duration: 20s;
  animation-delay: -4s;
}

@keyframes bubble-drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -40px) scale(1.05); }
  66% { transform: translate(-20px, 25px) scale(0.95); }
}

@media (prefers-reduced-motion: reduce) {
  .bg-bubble { animation: none; }
}

/* ===== Page Transition ===== */
.page-fade-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-fade-leave-active {
  transition: opacity 0.15s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-fade-leave-to {
  opacity: 0;
}
</style>
