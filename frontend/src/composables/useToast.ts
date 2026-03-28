import { reactive } from 'vue'

export interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
}

const toasts = reactive<ToastItem[]>([])
let nextId = 0

function addToast(message: string, type: ToastItem['type'], duration = 3000) {
  const id = ++nextId
  toasts.push({ id, message, type })
  setTimeout(() => {
    const index = toasts.findIndex((t) => t.id === id)
    if (index !== -1) toasts.splice(index, 1)
  }, duration)
}

export function useToast() {
  return {
    toasts,
    success: (msg: string) => addToast(msg, 'success'),
    error: (msg: string) => addToast(msg, 'error'),
    info: (msg: string) => addToast(msg, 'info'),
    warning: (msg: string) => addToast(msg, 'warning'),
  }
}
