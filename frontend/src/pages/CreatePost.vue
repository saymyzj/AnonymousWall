<template>
  <div class="create-page">
    <div class="create-header">
      <button class="back-btn" @click="$router.back()">←</button>
      <h2>发帖</h2>
      <button class="publish-btn" :disabled="!canPublish || loading" @click="publish">
        {{ loading ? '发布中...' : '发布' }}
      </button>
    </div>

    <div class="create-grid">
      <!-- Left: Edit Area -->
      <div class="edit-column">
        <div class="edit-card">
          <textarea
            v-model="content"
            placeholder="说点什么吧..."
            maxlength="500"
            rows="12"
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

        <!-- Future Features Placeholder -->
        <div class="section">
          <h3>更多选项</h3>
          <div class="future-options">
            <button class="future-btn" disabled title="即将上线">📊 投票</button>
            <button class="future-btn" disabled title="即将上线">💣 阅后即焚</button>
            <button class="future-btn" disabled title="即将上线">📎 附件</button>
          </div>
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      </div>

      <!-- Right: Live Preview -->
      <div class="preview-column">
        <h3 class="preview-title">预览</h3>
        <div class="preview-card" :class="`bubble-${bgColor}`">
          <div class="preview-header">
            <div class="preview-avatar">?</div>
            <span class="preview-nick">匿名用户</span>
            <span class="preview-time">刚刚</span>
          </div>
          <p class="preview-content" :class="{ placeholder: !content }">
            {{ content || '在左侧输入内容，预览将在这里实时显示...' }}
          </p>
          <div v-if="tag" class="preview-tag">
            <span class="tag-capsule">{{ tagEmoji(tag) }} {{ tag }}</span>
          </div>
          <div class="preview-actions">
            <span>♡ 0</span>
            <span>💬 0</span>
          </div>
        </div>
      </div>
    </div>
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

function tagEmoji(tagVal: string) {
  const map: Record<string, string> = {
    '表白': '💌', '吐槽': '😤', '求助': '🆘',
    '树洞': '🕳️', '失物招领': '🔍', '搭子': '🤝',
  }
  return map[tagVal] || ''
}

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
  max-width: 900px;
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
  transition: transform 0.2s ease;
}

.back-btn:hover {
  transform: translateX(-2px);
  box-shadow: none;
}

.publish-btn {
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.publish-btn:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(124, 92, 252, 0.3);
}

.publish-btn:disabled {
  opacity: 0.5;
}

/* Dual-column grid */
.create-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-5);
}

@media (min-width: 768px) {
  .create-grid {
    grid-template-columns: 1fr 1fr;
    gap: var(--space-8);
    align-items: start;
  }

  .preview-column {
    position: sticky;
    top: 80px;
  }
}

/* Edit Area */
.edit-card {
  background: var(--card-bg);
  border-radius: var(--card-radius);
  padding: var(--space-4);
  margin-bottom: var(--space-5);
  border: 1px solid var(--divider);
  transition: border-color 0.2s ease;
}

.edit-card:focus-within {
  border-color: var(--brand-primary);
}

.edit-card textarea {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  font-size: 15px;
  line-height: 24px;
  color: var(--text-primary);
  resize: none;
  font-family: inherit;
  min-height: 240px;
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

.tag-option:hover:not(.active) {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
  background: var(--brand-primary-light);
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

.color-dot:hover {
  transform: scale(1.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.color-dot.active {
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 2px white, 0 0 0 4px var(--brand-primary);
  transform: scale(1.15);
}

/* Future options placeholder */
.future-options {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.future-btn {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px dashed var(--divider);
  background: transparent;
  color: var(--text-placeholder);
  font-size: 13px;
  cursor: not-allowed;
}

/* Preview Column */
.preview-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: var(--space-3);
  color: var(--text-secondary);
}

.preview-card {
  border-radius: var(--card-radius);
  padding: var(--space-5);
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.preview-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a78bfa, #7c5cfc);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: 600;
}

.preview-nick {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.preview-time {
  font-size: 12px;
  color: var(--text-secondary);
  margin-left: auto;
}

.preview-content {
  font-size: 15px;
  line-height: 24px;
  margin-bottom: var(--space-3);
  word-break: break-word;
  white-space: pre-wrap;
}

.preview-content.placeholder {
  color: var(--text-placeholder);
  font-style: italic;
}

.preview-tag { margin-bottom: var(--space-3); }
.tag-capsule {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.06);
  color: var(--text-secondary);
}

.preview-actions {
  display: flex;
  gap: var(--space-6);
  font-size: 13px;
  color: var(--text-secondary);
}

.error-msg {
  color: var(--color-error);
  font-size: 13px;
  text-align: center;
}
</style>
