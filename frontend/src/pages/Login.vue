<template>
  <div class="login-page">
    <!-- Animated bubbles background -->
    <div class="bubbles-bg">
      <div v-for="n in 8" :key="n" class="bubble" :class="`bubble-anim-${n}`"></div>
    </div>

    <div class="login-card">
      <h1 class="logo-text">AnonymousWall</h1>
      <p class="subtitle">匿名树洞 · 说出你的心声</p>

      <!-- Tabs -->
      <div class="tabs">
        <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
        <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="input-group">
          <input
            v-model="email"
            type="email"
            placeholder="请输入邮箱"
            required
          />
        </div>
        <div class="input-group">
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码（8位以上，含字母和数字）"
            required
            minlength="8"
          />
        </div>
        <template v-if="mode === 'register'">
          <div class="input-group">
            <input
              v-model="studentId"
              type="text"
              placeholder="请输入学号/工号"
              required
            />
          </div>
          <div class="input-group">
            <input
              v-model="realName"
              type="text"
              placeholder="请输入真实姓名"
              required
            />
          </div>
        </template>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '请稍候...' : (mode === 'login' ? '登录' : '注册') }}
        </button>
      </form>

      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const mode = ref<'login' | 'register'>('login')
const email = ref('')
const password = ref('')
const studentId = ref('')
const realName = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    if (mode.value === 'login') {
      await authStore.login(email.value, password.value)
    } else {
      await authStore.register(email.value, password.value, studentId.value, realName.value)
    }
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: any) {
    errorMsg.value = e.response?.data?.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
}

.bubbles-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  background: var(--brand-primary);
}

.bubble-anim-1 { width: 80px; height: 80px; top: 10%; left: 10%; animation: float 6s ease-in-out infinite; }
.bubble-anim-2 { width: 60px; height: 60px; top: 20%; right: 15%; animation: float 8s ease-in-out infinite 1s; background: var(--brand-secondary); }
.bubble-anim-3 { width: 100px; height: 100px; bottom: 20%; left: 20%; animation: float 7s ease-in-out infinite 2s; }
.bubble-anim-4 { width: 50px; height: 50px; bottom: 30%; right: 25%; animation: float 9s ease-in-out infinite 0.5s; background: var(--color-success); }
.bubble-anim-5 { width: 70px; height: 70px; top: 50%; left: 5%; animation: float 6.5s ease-in-out infinite 1.5s; background: var(--brand-secondary); }
.bubble-anim-6 { width: 40px; height: 40px; top: 5%; left: 50%; animation: float 7.5s ease-in-out infinite 3s; }
.bubble-anim-7 { width: 90px; height: 90px; bottom: 10%; right: 10%; animation: float 8.5s ease-in-out infinite 2.5s; background: var(--color-info); }
.bubble-anim-8 { width: 55px; height: 55px; top: 40%; right: 5%; animation: float 5.5s ease-in-out infinite 4s; background: var(--color-warning); }

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: var(--card-radius);
  padding: var(--space-8) var(--space-6);
  box-shadow: var(--shadow-lg);
  position: relative;
  z-index: 1;
}

.logo-text {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-primary);
  margin-bottom: var(--space-2);
}

.subtitle {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
}

.tabs {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  justify-content: center;
}

.tabs button {
  background: none;
  border: none;
  font-size: 16px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--space-2) var(--space-4);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tabs button.active {
  color: var(--brand-primary);
  border-bottom-color: var(--brand-primary);
  font-weight: 600;
}

.input-group {
  margin-bottom: var(--space-4);
}

.input-group input {
  width: 100%;
  height: 48px;
  border: 1px solid var(--divider);
  border-radius: 16px;
  padding: 0 var(--space-4);
  font-size: 15px;
  background: transparent;
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.2s;
}

.input-group input:focus {
  border-color: var(--brand-primary);
}

.input-group input::placeholder {
  color: var(--text-placeholder);
}

.submit-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--brand-primary), #9B7BFC);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: var(--space-2);
}

.submit-btn:disabled {
  opacity: 0.6;
}

.submit-btn:active {
  transform: scale(0.98);
}

.error-msg {
  text-align: center;
  color: var(--color-error);
  font-size: 13px;
  margin-top: var(--space-3);
}
</style>
