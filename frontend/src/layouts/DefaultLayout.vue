<template>
  <div class="layout">
    <!-- Navbar -->
    <nav class="navbar">
      <router-link to="/" class="logo">AnonymousWall</router-link>
      <div class="nav-right">
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
    </nav>

    <!-- Content -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- FAB -->
    <button
      v-if="authStore.isLoggedIn"
      class="fab"
      @click="$router.push('/create')"
    >
      +
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const avatarText = computed(() => {
  const nick = authStore.identity?.nickname || '?'
  return nick.charAt(2) || nick.charAt(0)
})

const avatarColor = computed(() => {
  const seed = authStore.identity?.avatar_seed || '000'
  const hex = seed.substring(0, 6)
  return `#${hex}`
})
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
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.fab:active {
  transform: scale(0.9);
}

@media (min-width: 768px) {
  .navbar {
    height: 64px;
    padding: 0 var(--space-6);
  }
}
</style>
