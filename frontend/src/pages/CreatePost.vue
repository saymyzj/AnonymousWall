<template>
  <div class="create-page">
    <div class="create-header">
      <button class="back-btn" @click="$router.back()">← 返回</button>
      <h2>发帖</h2>
      <button class="publish-btn" :disabled="!canPublish || loading" @click="publish">
        {{ loading ? '发布中...' : '发布' }}
      </button>
    </div>

    <div class="create-grid">
      <!-- Left: Editor -->
      <div class="editor-col">
        <div class="editor-card">
          <textarea
            v-model="content"
            placeholder="说点什么吧..."
            maxlength="500"
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

        <!-- Future Features -->
        <div class="section">
          <h3>更多选项</h3>
          <div class="future-row">
            <button class="future-btn" disabled title="即将上线">📊 投票</button>
            <button class="future-btn" disabled title="即将上线">💣 阅后即焚</button>
            <button class="future-btn" disabled title="即将上线">📎 附件</button>
          </div>
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      </div>

      <!-- Right: Live Preview -->
      <div class="preview-col">
        <h3 class="preview-label">预览效果</h3>
        <div class="preview-bubble" :class="`bubble-${bgColor}`">
          <div class="pv-header">
            <div class="pv-avatar">?</div>
            <div class="pv-meta">
              <span class="pv-nick">匿名用户</span>
              <span class="pv-time">刚刚</span>
            </div>
          </div>
          <p class="pv-content" :class="{ empty: !content }">
            {{ content || '在左侧输入内容，预览将实时显示...' }}
          </p>
          <div class="pv-footer">
            <span v-if="tag" class="tag-capsule">{{ tagEmoji(tag) }} {{ tag }}</span>
            <div class="pv-stats">
              <span>♡ 0</span>
              <span>💬 0</span>
            </div>
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
  max-width: 960px;
  margin: 0 auto;
}

.create-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.create-header h2 {
  font-size: 20px;
  font-weight: 600;
}

.back-btn {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  color: var(--text-secondary);
  font-weight: 500;
  transition: color 0.2s;
}

.back-btn:hover {
  color: var(--brand-primary);
  transform: none;
}

.publish-btn {
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 28px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.publish-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(124, 92, 252, 0.3);
}

.publish-btn:disabled {
  opacity: 0.4;
}

/* Grid */
.create-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 36px;
  align-items: start;
}

/* Editor */
.editor-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1.5px solid var(--divider);
  transition: border-color 0.2s;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.editor-card:focus-within {
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px rgba(124, 92, 252, 0.08);
}

.editor-card textarea {
  width: 100%;
  min-height: 280px;
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
  color: var(--text-placeholder);
  margin-top: 8px;
}

.section {
  margin-bottom: 24px;
}

.section h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.tag-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-option {
  padding: 7px 16px;
  border-radius: 999px;
  border: 1.5px solid var(--divider);
  background: white;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-option:hover:not(.active) {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.tag-option.active {
  background: var(--brand-primary);
  color: white;
  border-color: var(--brand-primary);
}

.color-options {
  display: flex;
  gap: 12px;
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
  transform: scale(1.3);
}

.color-dot.active {
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 2px white, 0 0 0 4px var(--brand-primary);
  transform: scale(1.15);
}

.future-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.future-btn {
  padding: 7px 16px;
  border-radius: 999px;
  border: 1.5px dashed var(--divider);
  background: transparent;
  color: var(--text-placeholder);
  font-size: 13px;
  cursor: not-allowed;
}

.error-msg {
  color: var(--color-error);
  font-size: 13px;
  text-align: center;
}

/* Preview */
.preview-col {
  position: sticky;
  top: 88px;
}

.preview-label {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.preview-bubble {
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.pv-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.pv-avatar {
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

.pv-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.pv-nick {
  font-size: 13px;
  font-weight: 600;
}

.pv-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.pv-content {
  font-size: 15px;
  line-height: 24px;
  margin-bottom: 14px;
  word-break: break-word;
  white-space: pre-wrap;
}

.pv-content.empty {
  color: var(--text-placeholder);
  font-style: italic;
}

.pv-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tag-capsule {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.06);
  color: var(--text-secondary);
}

.pv-stats {
  display: flex;
  gap: 14px;
  font-size: 13px;
  color: var(--text-secondary);
  opacity: 0.6;
}
</style>
