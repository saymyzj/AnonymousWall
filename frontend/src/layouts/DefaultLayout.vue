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

    <!-- Content -->
    <main class="main-content">
      <router-view />
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
  height: 56px;
  padding: 0 var(--space-4);
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
  padding: var(--space-4);
  max-width: 960px;
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

.fab:active {
  transform: scale(0.9);
}

.fab.hidden {
  transform: translateY(80px);
  opacity: 0;
  pointer-events: none;
}

@media (min-width: 768px) {
  .navbar {
    height: 64px;
    padding: 0 var(--space-6);
  }
}
</style>
