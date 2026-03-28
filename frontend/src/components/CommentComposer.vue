<template>
  <div class="comment-input-box" :class="{ inline }" ref="composerEl" @focusout="handleFocusOut">
    <div class="ci-top">
      <div class="ci-avatar">{{ avatarText }}</div>
      <span class="ci-label">以匿名身份评论</span>
    </div>

    <div v-if="replyLabel" class="reply-hint">
      <span>正在回复 {{ replyLabel }}</span>
      <button type="button" @click="$emit('cancel-reply')">取消</button>
    </div>

    <textarea
      ref="textareaEl"
      :value="modelValue"
      class="ci-textarea"
      maxlength="200"
      placeholder="写下你想说的话..."
      @input="handleInput"
      @keydown.enter.exact.prevent="$emit('submit')"
    ></textarea>

    <div class="ci-toolbar">
      <span class="ci-char">{{ modelValue.length }} / 200</span>
      <button class="ci-submit" type="button" :disabled="!modelValue.trim() || submitting" @click="$emit('submit')">
        {{ submitting ? '发布中...' : '发布评论' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: string
  avatarText: string
  submitting?: boolean
  replyLabel?: string
  autofocus?: boolean
  inline?: boolean
}>(), {
  submitting: false,
  replyLabel: '',
  autofocus: false,
  inline: false,
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel-reply', 'blur-exit'])

const composerEl = ref<HTMLDivElement>()
const textareaEl = ref<HTMLTextAreaElement>()

function resizeTextarea() {
  if (!textareaEl.value) return
  textareaEl.value.style.height = 'auto'
  textareaEl.value.style.height = `${Math.min(textareaEl.value.scrollHeight, 160)}px`
}

function focusComposer() {
  if (!textareaEl.value) return
  composerEl.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'nearest',
  })
  textareaEl.value.focus()
  const length = textareaEl.value.value.length
  textareaEl.value.setSelectionRange(length, length)
}

function handleInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLTextAreaElement).value)
}

function handleFocusOut(event: FocusEvent) {
  if (!props.inline || props.submitting) return
  const nextTarget = event.relatedTarget as Node | null
  if (nextTarget && composerEl.value?.contains(nextTarget)) return
  emit('blur-exit')
}

watch(
  () => props.modelValue,
  async () => {
    await nextTick()
    resizeTextarea()
  },
  { immediate: true },
)

onMounted(async () => {
  await nextTick()
  resizeTextarea()
  if (props.autofocus) {
    focusComposer()
  }
})
</script>

<style scoped>
.comment-input-box {
  background: var(--glass-bg);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 20px;
  margin-bottom: 28px;
  backdrop-filter: blur(8px);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.comment-input-box.inline {
  margin: 14px 0 12px 50px;
}

.comment-input-box:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--glow-brand);
}

.ci-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.ci-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--gradient-avatar);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
}

.ci-label {
  font-size: 0.875rem;
  color: var(--text-2);
}

.reply-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--brand);
  font-size: 0.8125rem;
  margin-bottom: 10px;
}

.reply-hint button {
  border: 0;
  background: transparent;
  color: var(--text-2);
}

.reply-hint button:hover {
  color: var(--text-1);
}

.ci-textarea {
  width: 100%;
  padding: 12px 0;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-1);
  font-size: 0.9375rem;
  font-family: var(--font-sans);
  resize: none;
  min-height: 48px;
  max-height: 160px;
  border-bottom: 1px solid var(--divider);
}

.ci-textarea::placeholder {
  color: var(--text-3);
}

.ci-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
}

.ci-char {
  font-size: 0.75rem;
  color: var(--text-3);
}

.ci-submit {
  padding: 8px 24px;
  border-radius: var(--radius-pill);
  background: var(--brand);
  color: #fff;
  border: none;
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 6px 16px var(--glow-brand);
}

.ci-submit:hover:not(:disabled) {
  background: var(--brand-deep);
  box-shadow: 0 8px 24px var(--glow-brand);
}

.ci-submit:disabled {
  opacity: 0.45;
}

@media (max-width: 599px) {
  .comment-input-box.inline {
    margin-left: 20px;
  }
}
</style>
