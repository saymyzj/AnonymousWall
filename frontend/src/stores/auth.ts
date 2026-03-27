import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

interface Identity {
  id: number
  nickname: string
  avatar_seed: string
  created_at: string
}

interface UserInfo {
  id: number
  email: string
  student_id: string
  real_name: string
  is_verified: boolean
  is_banned: boolean
  ban_until: string | null
  date_joined: string
  theme_preference: 'system' | 'dark' | 'light'
  default_identity: Identity | null
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!accessToken.value)
  const isVerified = computed(() => !!userInfo.value?.is_verified)
  const identity = computed(() => userInfo.value?.default_identity)

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  async function login(email: string, password: string) {
    const res = await authApi.login(email, password)
    const data = res.data.data
    setTokens(data.access, data.refresh)
    userInfo.value = data.user
    return data
  }

  async function register(email: string, password: string, studentId: string, realName?: string) {
    const res = await authApi.register({ email, password, student_id: studentId, real_name: realName })
    const data = res.data.data
    setTokens(data.access, data.refresh)
    userInfo.value = data.user
    return data
  }

  async function updatePreferences(data: Partial<Pick<UserInfo, 'theme_preference' | 'real_name' | 'student_id'>>) {
    const res = await authApi.updatePreferences(data)
    userInfo.value = res.data.data
    return res.data.data
  }

  async function refreshIdentity() {
    const res = await authApi.refreshIdentity()
    userInfo.value = res.data.data
    return res.data.data
  }

  async function fetchMe() {
    if (!accessToken.value) return
    try {
      const res = await authApi.getMe()
      userInfo.value = res.data.data
    } catch {
      logout()
    }
  }

  function logout() {
    accessToken.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    accessToken, refreshToken, userInfo, isLoggedIn, isVerified, identity,
    setTokens, login, register, fetchMe, updatePreferences, refreshIdentity, logout,
  }
})
