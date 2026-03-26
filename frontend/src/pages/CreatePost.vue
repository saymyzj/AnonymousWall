<template>
  <div class="create-page">
    <div class="create-header">
      <button class="back-btn" @click="$router.back()">←</button>
      <h2>发帖</h2>
      <button class="publish-btn" :disabled="!canPublish || loading" @click="publish">
        {{ loading ? '发布中...' : '发布' }}
      </button>
    </div>

    <!-- Preview Card -->
    <div class="preview-card" :class="`bubble-${bgColor}`">
      <textarea
        v-model="content"
        placeholder="说点什么吧..."
        maxlength="500"
        rows="6"
      ></textarea>
      <div class="char-count">{{ content.length }}/500</div>
    </div>

    <!-- Tag Selection -->
    <div class="section">
      <h3>标签（必选一个）</h3>
      <div class="tag-options">
        <button
          v-for="t in tagOptions"
          :key="t.value"
          class="tag-option"
          :class="{ active: tag === t.value }"
          @click="tag = t.value"
        >
          {{ t.emoji }} {{ t.label }}
        </button>
      </div>
    </div>

    <!-- Background Color -->
    <div class="section">
      <h3>背景色</h3>
      <div class="color-options">
        <button
          v-for="c in colorOptions"
          :key="c.value"
          class="color-dot"
          :class="[`bubble-${c.value}`, { active: bgColor === c.value }]"
          @click="bgColor = c.value"
        ></button>
      </div>
    </div>

    <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { postsApi } from '../api/posts'
import { showToast } from 'vant'

const router = useRouter()
const content = ref('')
const tag = ref('')
const bgColor = ref(7)
const loading = ref(false)
const errorMsg = ref('')

const canPublish = computed(() => content.value.trim().length > 0 && tag.value)

const tagOptions = [
  { label: '表白', value: '表白', emoji: '💌' },
  { label: '吐槽', value: '吐槽', emoji: '😤' },
  { label: '求助', value: '求助', emoji: '🆘' },
  { label: '树洞', value: '树洞', emoji: '🕳️' },
  { label: '失物招领', value: '失物招领', emoji: '🔍' },
  { label: '搭子', value: '搭子', emoji: '🤝' },
]

const colorOptions = [
  { value: 1 }, { value: 2 }, { value: 3 }, { value: 4 },
  { value: 5 }, { value: 6 }, { value: 7 }, { value: 8 },
]

async function publish() {
  errorMsg.value = ''
  loading.value = true
  try {
    await postsApi.create({
      content: content.value,
      tag: tag.value,
      bg_color: bgColor.value,
    })
    showToast('发布成功')
    router.push('/')
  } catch (e: any) {
    errorMsg.value = e.response?.data?.message || '发布失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.create-page {
  max-width: 600px;
  margin: 0 auto;
}

.create-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}

.create-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.back-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-primary);
}

.publish-btn {
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.publish-btn:disabled {
  opacity: 0.5;
}

.preview-card {
  border-radius: var(--card-radius);
  padding: var(--space-4);
  margin-bottom: var(--space-5);
  position: relative;
}

.preview-card textarea {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  font-size: 15px;
  line-height: 24px;
  color: var(--text-primary);
  resize: none;
  font-family: inherit;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: var(--space-2);
}

.section {
  margin-bottom: var(--space-5);
}

.section h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: var(--space-3);
  color: var(--text-primary);
}

.tag-options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tag-option {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--divider);
  background: var(--card-bg);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-option.active {
  background: var(--brand-primary);
  color: white;
  border-color: var(--brand-primary);
  transform: scale(1.05);
}

.color-options {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.color-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.color-dot.active {
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 2px white, 0 0 0 4px var(--brand-primary);
  transform: scale(1.15);
}

.error-msg {
  color: var(--color-error);
  font-size: 13px;
  text-align: center;
}
</style>
