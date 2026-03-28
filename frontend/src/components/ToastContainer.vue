<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast-item"
          :class="toast.type"
        >
          <span class="toast-icon">{{ icon(toast.type) }}</span>
          <span class="toast-msg">{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '../composables/useToast'

const { toasts } = useToast()

function icon(type: string) {
  switch (type) {
    case 'success': return '✓'
    case 'error': return '✕'
    case 'warning': return '⚠'
    case 'info': return 'ℹ'
    default: return ''
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  pointer-events: none;
}

.toast-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 22px;
  border-radius: var(--radius-pill, 999px);
  font-size: 0.875rem;
  font-weight: 600;
  backdrop-filter: blur(20px);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.2);
  pointer-events: auto;
  max-width: 420px;
}

.toast-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 800;
  flex-shrink: 0;
}

.toast-item.success {
  background: rgba(6, 214, 160, 0.18);
  border: 1px solid rgba(6, 214, 160, 0.3);
  color: #06d6a0;
}

.toast-item.success .toast-icon {
  background: rgba(6, 214, 160, 0.25);
}

.toast-item.error {
  background: rgba(248, 113, 113, 0.18);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
}

.toast-item.error .toast-icon {
  background: rgba(248, 113, 113, 0.25);
}

.toast-item.warning {
  background: rgba(251, 191, 36, 0.18);
  border: 1px solid rgba(251, 191, 36, 0.3);
  color: #fbbf24;
}

.toast-item.warning .toast-icon {
  background: rgba(251, 191, 36, 0.25);
}

.toast-item.info {
  background: rgba(96, 165, 250, 0.18);
  border: 1px solid rgba(96, 165, 250, 0.3);
  color: #60a5fa;
}

.toast-item.info .toast-icon {
  background: rgba(96, 165, 250, 0.25);
}

/* Light mode adjustments */
:root[data-theme='light'] .toast-item {
  box-shadow: 0 12px 36px rgba(79, 70, 126, 0.14);
}

:root[data-theme='light'] .toast-item.success {
  background: rgba(6, 214, 160, 0.12);
  color: #059669;
}

:root[data-theme='light'] .toast-item.error {
  background: rgba(248, 113, 113, 0.12);
  color: #dc2626;
}

:root[data-theme='light'] .toast-item.warning {
  background: rgba(251, 191, 36, 0.12);
  color: #d97706;
}

:root[data-theme='light'] .toast-item.info {
  background: rgba(96, 165, 250, 0.12);
  color: #2563eb;
}

/* Transition */
.toast-enter-active {
  transition: all 0.35s cubic-bezier(0.21, 1.02, 0.73, 1);
}

.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.92);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.96);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
