<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useTheme } from './composables/useTheme'

const authStore = useAuthStore()
const { initTheme } = useTheme()

onMounted(() => {
  initTheme()
  if (authStore.isLoggedIn) {
    authStore.fetchMe().then(() => {
      initTheme(authStore.userInfo?.theme_preference)
    })
  }
})
</script>
