import { computed, ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

const STORAGE_KEY = 'anonymouswall-theme'
const themePreference = ref<'system' | 'dark' | 'light'>(
  (localStorage.getItem(STORAGE_KEY) as 'system' | 'dark' | 'light') || 'system',
)

function resolveTheme(preference: 'system' | 'dark' | 'light') {
  if (preference === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return preference
}

function applyTheme(preference: 'system' | 'dark' | 'light') {
  const resolved = resolveTheme(preference)
  document.documentElement.dataset.theme = resolved
}

export function useTheme() {
  const authStore = useAuthStore()

  const resolvedTheme = computed(() => resolveTheme(themePreference.value))

  function setTheme(next: 'system' | 'dark' | 'light') {
    themePreference.value = next
    localStorage.setItem(STORAGE_KEY, next)
    applyTheme(next)
    if (authStore.isLoggedIn) {
      authStore.updatePreferences({ theme_preference: next }).catch(() => undefined)
    }
  }

  function cycleTheme() {
    const order: Array<'system' | 'dark' | 'light'> = ['system', 'dark', 'light']
    const currentIndex = order.indexOf(themePreference.value)
    const next = order[(currentIndex + 1) % order.length]
    setTheme(next)
  }

  function initTheme(preference?: 'system' | 'dark' | 'light') {
    if (preference) {
      themePreference.value = preference
      localStorage.setItem(STORAGE_KEY, preference)
    }
    applyTheme(themePreference.value)
  }

  watch(themePreference, (value) => {
    applyTheme(value)
  })

  return {
    themePreference,
    resolvedTheme,
    setTheme,
    cycleTheme,
    initTheme,
  }
}
