<template>
  <div class="layout">
    <!-- Navbar -->
    <nav class="navbar" :class="{ 'search-mode': isSearching }">
      <template v-if="isSearching">
        <div class="search-bar">
          <span class="search-icon-inner">🔍</span>
          <input
            ref="searchInput"
            v-model="searchQuery"
            placeholder="搜索匿名心声..."
            @keyup.enter="doSearch"
          />
          <button class="search-close" @click="closeSearch">×</button>
        </div>
      </template>
      <template v-else>
        <router-link to="/" class="logo">🫧 AnonymousWall</router-link>
        <div class="nav-right">
          <button class="nav-icon" @click="openSearch">🔍</button>
          <template v-if="authStore.isLoggedIn">
            <router-link to="/profile" class="nav-avatar">
              <div class="avatar-circle" :style="{ background: avatarColor }">
                {{ avatarText }}
              </div>
            </router-link>
          </template>
          <template v-else>
            <router-link to="/login" class="login-btn">登录</router-link>
          </template>
        </div>
      </template>
    </nav>

    <!-- Background Decorative Bubbles -->
    <div class="bg-bubbles" aria-hidden="true">
      <div class="bg-bubble b1"></div>
      <div class="bg-bubble b2"></div>
      <div class="bg-bubble b3"></div>
      <div class="bg-bubble b4"></div>
      <div class="bg-bubble b5"></div>
    </div>

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
      +
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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
  const hex = seed.substring(0, 6)
  return `#${hex}`
})

// Search
const isSearching = ref(false)
const searchQuery = ref('')
const searchInput = ref<HTMLInputElement>()

function openSearch() {
  isSearching.value = true
  nextTick(() => searchInput.value?.focus())
}

function closeSearch() {
  isSearching.value = false
  if (searchQuery.value) {
    searchQuery.value = ''
    postsStore.setFilter('search', undefined)
  }
}

function doSearch() {
  const q = searchQuery.value.trim()
  if (q) {
    postsStore.setFilter('search', q)
    router.push('/')
  }
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
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 var(--space-8);
  background: var(--card-bg);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--divider);
}

.navbar.search-mode {
  padding: 0 var(--space-3);
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--brand-primary);
  text-decoration: none;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.nav-icon {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}

.login-btn {
  font-size: 14px;
  color: var(--brand-primary);
  font-weight: 600;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: 600;
}

/* Search bar */
.search-bar {
  display: flex;
  align-items: center;
  flex: 1;
  height: 44px;
  background: var(--card-bg);
  border: 1px solid var(--divider);
  border-radius: 16px;
  padding: 0 var(--space-3);
  gap: var(--space-2);
  animation: search-expand 0.3s ease-out;
}

@keyframes search-expand {
  from { opacity: 0; transform: scaleX(0.8); }
  to { opacity: 1; transform: scaleX(1); }
}

.search-icon-inner {
  font-size: 16px;
  flex-shrink: 0;
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

.search-close {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.main-content {
  padding: var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.fab {
  position: fixed;
  right: 20px;
  bottom: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, var(--brand-primary), #9B7BFC);
  color: white;
  font-size: 28px;
  font-weight: 300;
  cursor: pointer;
  box-shadow: var(--shadow-float);
  z-index: 99;
  transition: transform 0.3s, opacity 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 48px rgba(124, 92, 252, 0.25);
}

.fab:active {
  transform: scale(0.9);
}

.fab.hidden {
  transform: translateY(80px);
  opacity: 0;
  pointer-events: none;
}

.logo {
  font-size: 22px;
}

.logo:hover {
  opacity: 0.8;
}

.nav-icon:hover {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}

.login-btn:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.avatar-circle {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.nav-avatar:hover .avatar-circle {
  transform: scale(1.1);
  box-shadow: 0 0 0 2px var(--brand-primary);
}

/* Background Decorative Bubbles */
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
  opacity: 0.15;
  animation: bubble-float 20s ease-in-out infinite;
}

.bg-bubble.b1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #7C5CFC, transparent 70%);
  top: 10%;
  left: -5%;
  animation-duration: 25s;
}

.bg-bubble.b2 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #FF6B9D, transparent 70%);
  top: 60%;
  right: -3%;
  animation-duration: 20s;
  animation-delay: -5s;
}

.bg-bubble.b3 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, #34D399, transparent 70%);
  bottom: 5%;
  left: 30%;
  animation-duration: 22s;
  animation-delay: -10s;
}

.bg-bubble.b4 {
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, #60A5FA, transparent 70%);
  top: 30%;
  right: 20%;
  animation-duration: 18s;
  animation-delay: -3s;
}

.bg-bubble.b5 {
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, #FBBF24, transparent 70%);
  top: 5%;
  right: 40%;
  animation-duration: 24s;
  animation-delay: -8s;
}

@keyframes bubble-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(20px, -30px) scale(1.05); }
  50% { transform: translate(-15px, 20px) scale(0.95); }
  75% { transform: translate(10px, 15px) scale(1.02); }
}

@media (prefers-reduced-motion: reduce) {
  .bg-bubble {
    animation: none;
  }
}

/* Page Transition */
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
