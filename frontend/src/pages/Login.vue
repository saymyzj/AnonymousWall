<template>
  <div class="auth-page">
    <div class="left-panel">
      <div class="deco-bubble deco-bubble-1"></div>
      <div class="deco-bubble deco-bubble-2"></div>
      <div class="deco-bubble deco-bubble-3"></div>
      <div class="deco-bubble deco-bubble-4"></div>

      <div class="left-copy">
        <h1 class="left-tagline">
          每一个匿名气泡，
          <span class="highlight">都是星空中的一颗星</span>
        </h1>

        <div class="features">
          <div class="feature-item">
            <div class="feature-icon purple">🎭</div>
            <div>
              <div class="feature-title">完全匿名</div>
              <div class="feature-desc">以随机身份表达真实想法，前台身份与账号完全隔离。</div>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon pink">🫧</div>
            <div>
              <div class="feature-title">气泡表达</div>
              <div class="feature-desc">每条发言都像漂浮的宇宙气泡，轻盈但清晰地被看见。</div>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon cyan">🔒</div>
            <div>
              <div class="feature-title">安全守护</div>
              <div class="feature-desc">敏感词与审核机制协同工作，让匿名交流更安心。</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="right-panel">
      <div class="form-wrapper">
        <div class="form-header">
          <div class="form-logo">🫧 AnonymousWall</div>
          <div class="form-title">{{ mode === 'login' ? '欢迎回到宇宙' : '加入气泡宇宙' }}</div>
          <div class="form-subtitle">在这里，安全地说出你的心声。</div>
        </div>

        <div class="tab-pills">
          <button class="tab-pill" :class="{ active: mode === 'login' }" type="button" @click="mode = 'login'">登录</button>
          <button class="tab-pill" :class="{ active: mode === 'register' }" type="button" @click="mode = 'register'">注册</button>
        </div>

        <form v-if="mode === 'login'" class="form-panel active" @submit.prevent="handleSubmit">
          <div class="input-group">
            <label class="input-label">邮箱</label>
            <input v-model="email" class="input-field" type="email" placeholder="name@school.edu" required />
          </div>
          <div class="input-group">
            <label class="input-label">密码</label>
            <input
              v-model="password"
              class="input-field"
              type="password"
              placeholder="请输入密码"
              minlength="8"
              required
            />
          </div>
          <div class="options-row">
            <label class="remember-row">
              <input v-model="rememberMe" type="checkbox" />
              <span>记住我</span>
            </label>
          </div>
          <button class="submit-btn" type="submit" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <form v-else class="form-panel active" @submit.prevent="handleSubmit">
          <div class="input-group">
            <label class="input-label">邮箱</label>
            <input v-model="email" class="input-field" type="email" placeholder="name@school.edu" required />
          </div>
          <div class="input-group">
            <label class="input-label">学号</label>
            <input v-model="studentId" class="input-field" type="text" placeholder="请输入学号，管理员审核后才能使用全部功能" required />
          </div>
          <div class="input-group">
            <label class="input-label">真实姓名</label>
            <input v-model="realName" class="input-field" type="text" placeholder="用于后台实名审核，可后续修改" />
          </div>
          <div class="input-group">
            <label class="input-label">密码</label>
            <input
              v-model="password"
              class="input-field"
              type="password"
              placeholder="设置登录密码"
              minlength="8"
              required
            />
            <div class="password-strength">
              <span class="strength-seg" :class="strengthClass(0)"></span>
              <span class="strength-seg" :class="strengthClass(1)"></span>
              <span class="strength-seg" :class="strengthClass(2)"></span>
            </div>
            <div class="strength-text">密码需至少 8 位，包含字母和数字。</div>
          </div>
          <div class="input-group">
            <label class="input-label">确认密码</label>
            <input
              v-model="confirmPassword"
              class="input-field"
              type="password"
              placeholder="再次输入密码"
              minlength="8"
              required
            />
          </div>
          <button class="submit-btn" type="submit" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const mode = ref<'login' | 'register'>((route.query.mode as 'login' | 'register') || 'login')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const studentId = ref('')
const realName = ref('')
const rememberMe = ref(true)
const loading = ref(false)
const errorMsg = ref('')

const passwordStrength = computed(() => {
  let score = 0
  if (password.value.length >= 8) score += 1
  if (/[a-zA-Z]/.test(password.value) && /[0-9]/.test(password.value)) score += 1
  if (/[^a-zA-Z0-9]/.test(password.value) || password.value.length >= 12) score += 1
  return score
})

function strengthClass(index: number) {
  if (passwordStrength.value <= index) return ''
  if (passwordStrength.value === 1) return 'weak'
  if (passwordStrength.value === 2 && index < 2) return 'medium'
  return 'strong'
}

async function handleSubmit() {
  errorMsg.value = ''
  if (mode.value === 'register' && password.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  try {
    if (mode.value === 'login') {
      await authStore.login(email.value, password.value)
      if (!rememberMe.value) {
        sessionStorage.setItem('access_token', authStore.accessToken)
      }
    } else {
      await authStore.register(email.value, password.value, studentId.value, realName.value.trim())
    }
    router.push((route.query.redirect as string) || '/')
  } catch (error: any) {
    errorMsg.value = error.response?.data?.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr minmax(420px, 520px);
  background: var(--bg);
}

.left-panel,
.right-panel {
  position: relative;
  z-index: 1;
}

.left-panel {
  overflow: hidden;
  padding: 60px;
  display: flex;
  align-items: center;
}

.left-copy {
  position: relative;
  z-index: 1;
  max-width: 520px;
}

.deco-bubble {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
  backdrop-filter: blur(4px);
  animation: floatDeco var(--dur) ease-in-out infinite;
}

@keyframes floatDeco {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }

  50% {
    transform: translateY(-20px) scale(1.05);
  }
}

.deco-bubble-1 {
  top: 12%;
  left: 15%;
  width: 180px;
  height: 180px;
  background: linear-gradient(135deg, rgba(124, 92, 252, 0.2), rgba(255, 107, 157, 0.15));
  border: 1px solid rgba(124, 92, 252, 0.15);
  --dur: 8s;
}

.deco-bubble-2 {
  top: 55%;
  left: 60%;
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, rgba(6, 214, 160, 0.18), rgba(100, 230, 180, 0.12));
  border: 1px solid rgba(6, 214, 160, 0.12);
  --dur: 10s;
  animation-delay: 2s;
}

.deco-bubble-3 {
  top: 35%;
  left: 45%;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.18), rgba(255, 182, 193, 0.12));
  border: 1px solid rgba(255, 107, 157, 0.12);
  --dur: 7s;
  animation-delay: 1s;
}

.deco-bubble-4 {
  bottom: 20%;
  left: 20%;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, rgba(124, 92, 252, 0.15), rgba(180, 160, 255, 0.1));
  border: 1px solid rgba(124, 92, 252, 0.1);
  --dur: 9s;
  animation-delay: 3s;
}

.left-tagline {
  margin: 0 0 48px;
  font-size: 2rem;
  line-height: 1.5;
}

.highlight {
  background: linear-gradient(135deg, var(--brand), var(--pink));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-item {
  display: flex;
  gap: 16px;
}

.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.125rem;
}

.feature-icon.purple {
  background: rgba(124, 92, 252, 0.15);
}

.feature-icon.pink {
  background: rgba(255, 107, 157, 0.15);
}

.feature-icon.cyan {
  background: rgba(6, 214, 160, 0.15);
}

.feature-title {
  margin-bottom: 4px;
  font-size: 0.9375rem;
  font-weight: 600;
}

.feature-desc {
  color: var(--text-2);
  font-size: 0.8125rem;
  line-height: 1.6;
}

.right-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: 36px;
}

.form-logo {
  margin-bottom: 8px;
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--brand), var(--pink));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.form-title {
  margin-bottom: 6px;
  font-size: 1.5rem;
  font-weight: 700;
}

.form-subtitle {
  color: var(--text-2);
  font-size: 0.875rem;
}

.tab-pills {
  display: inline-flex;
  margin-bottom: 32px;
  padding: 4px;
  border-radius: var(--radius-pill);
  background: var(--bg-card);
}

.tab-pill {
  min-height: 42px;
  padding: 0 28px;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--text-3);
}

.tab-pill.active {
  background: var(--brand);
  color: #fff;
  box-shadow: 0 2px 12px rgba(124, 92, 252, 0.25);
}

.input-group {
  margin-bottom: 20px;
}

.input-label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-2);
  font-size: 0.8125rem;
  font-weight: 500;
}

.input-field {
  width: 100%;
  min-height: 50px;
  padding: 0 18px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-1);
  outline: none;
}

.input-field::placeholder {
  color: var(--text-3);
}

.input-field:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(124, 92, 252, 0.25);
}

.verify-row {
  display: flex;
  gap: 12px;
}

.verify-row .input-field {
  flex: 1;
}

.verify-btn {
  min-width: 108px;
  border: 1px solid rgba(124, 92, 252, 0.3);
  border-radius: 16px;
  background: rgba(124, 92, 252, 0.15);
  color: var(--brand);
}

.password-strength {
  display: flex;
  gap: 6px;
  height: 4px;
  margin-top: 10px;
}

.strength-seg {
  flex: 1;
  border-radius: 999px;
  background: var(--bg-card-hover);
}

.strength-seg.weak {
  background: #ff6b6b;
}

.strength-seg.medium {
  background: #ffc93c;
}

.strength-seg.strong {
  background: var(--cyan);
}

.strength-text {
  margin-top: 6px;
  color: var(--text-3);
  font-size: 0.75rem;
}

.options-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.remember-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-2);
  font-size: 0.8125rem;
}

.submit-btn {
  width: 100%;
  min-height: 50px;
  border: 0;
  border-radius: var(--radius-pill);
  background: linear-gradient(135deg, var(--brand), var(--pink));
  color: #fff;
  font-size: 0.9375rem;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(124, 92, 252, 0.22);
}

.submit-btn:disabled {
  opacity: 0.6;
}

.error-msg {
  margin-top: 16px;
  color: var(--pink);
  font-size: 0.8125rem;
}

@media (max-width: 768px) {
  .auth-page {
    grid-template-columns: 1fr;
  }

  .left-panel {
    display: none;
  }
}
</style>
