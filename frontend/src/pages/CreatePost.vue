<template>
  <div class="create-page">
    <div class="page-actions">
      <button class="ghost-pill" type="button" @click="saveDraft">存草稿</button>
      <button class="pill-button brand" type="button" :disabled="!canPublish || loading" @click="publish">
        {{ loading ? '发布中...' : '发布 ✦' }}
      </button>
    </div>

    <div class="layout">
      <section class="editor">
        <h1 class="editor-title"><span>✨</span> 创建新气泡</h1>

        <div class="field">
          <div class="field-label">匿名身份</div>
          <div class="identity-bar">
            <div class="id-avatar">{{ avatarText }}</div>
            <div>
              <div class="id-name">{{ authStore.identity?.nickname || '匿名气泡' }}</div>
              <div class="id-sub">仅用于本次发布</div>
            </div>
            <button class="id-refresh" type="button" @click="refreshIdentity">🎲 换</button>
          </div>
        </div>

        <div class="field">
          <div class="field-label">内容 <span class="req">*</span></div>
          <textarea
            v-model="content"
            rows="6"
            maxlength="500"
            placeholder="写下你想对世界说的话..."
          ></textarea>
          <div class="count-row">
            <span :class="{ warn: content.length > 450 }">{{ content.length }} / 500</span>
          </div>
        </div>

        <div class="field">
          <div class="field-label">标签 <span class="req">*</span></div>
          <div class="tags">
            <button
              v-for="option in tagOptions"
              :key="option.value"
              class="tag"
              :class="{ active: tag === option.value }"
              type="button"
              @click="tag = option.value"
            >
              {{ option.emoji }} {{ option.label }}
            </button>
          </div>
        </div>

        <div class="field">
          <div class="field-label">气泡配色</div>
          <div class="colors">
            <button
              v-for="option in colorOptions"
              :key="option.value"
              class="cdot"
              :class="[option.className, { active: bgColor === option.value }]"
              type="button"
              @click="bgColor = option.value"
            ></button>
          </div>
        </div>

        <div class="field">
          <div class="field-label">图片 <span class="sub">（可选，最多 3 张）</span></div>
          <div class="img-row">
            <label
              v-for="(image, index) in previewImages"
              :key="index"
              class="img-box"
              :class="{ filled: !!image }"
            >
              <template v-if="image">
                <img :src="image" alt="" />
                <button class="rm" type="button" @click.prevent="removeImage(index)">✕</button>
              </template>
              <template v-else>
                <span class="plus">+</span>
                <span>上传</span>
              </template>
              <input
                class="visually-hidden"
                type="file"
                accept="image/png,image/jpeg,image/webp"
                @change="onSelectImage($event, index)"
              />
            </label>
          </div>
        </div>

        <div class="field">
          <div class="field-label">⏱️ 自毁时间</div>
          <div class="timer-row">
            <button
              v-for="option in destroyOptions"
              :key="option.label"
              class="tc"
              :class="{ active: destroyAfterHours === option.value }"
              type="button"
              @click="destroyAfterHours = option.value"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <div class="field">
          <div class="tgl-row">
            <div class="tgl-txt">允许匿名私信</div>
            <button class="tgl" :class="{ on: allowMessages }" type="button" @click="allowMessages = !allowMessages"></button>
          </div>
          <div class="tgl-row">
            <div class="tgl-txt">附加投票</div>
            <button class="tgl" :class="{ on: pollEnabled }" type="button" @click="pollEnabled = !pollEnabled"></button>
          </div>
        </div>

        <div v-if="pollEnabled" class="field poll-builder">
          <div class="field-label">投票设置</div>
          <input v-model="pollQuestion" class="poll-input" type="text" maxlength="120" placeholder="投票问题（可选）" />
          <div class="poll-options">
            <input
              v-for="(_, index) in pollOptions"
              :key="index"
              v-model="pollOptions[index]"
              class="poll-input"
              type="text"
              maxlength="30"
              :placeholder="`选项 ${index + 1}`"
            />
          </div>
          <div class="poll-builder-actions">
            <button v-if="pollOptions.length < 6" class="ghost-pill" type="button" @click="pollOptions.push('')">新增选项</button>
            <select v-model="pollExpireDays" class="poll-select">
              <option :value="1">1 天</option>
              <option :value="3">3 天</option>
              <option :value="7">7 天</option>
            </select>
          </div>
        </div>

        <p v-if="notice" class="notice">{{ notice }}</p>
      </section>

      <aside class="preview">
        <div class="preview-title">✦ 实时预览</div>

        <article class="preview-bubble bubble-surface" :class="`bubble-${bgColor}`">
          <div class="p-tag">{{ currentTagLabel }}</div>
          <div class="p-content" :class="{ placeholder: !content.trim() }">
            {{ content.trim() || '你的气泡内容将显示在这里...' }}
          </div>

          <div v-if="filledPreviewImages.length" class="p-images">
            <div v-for="image in filledPreviewImages" :key="image" class="p-img">
              <img :src="image" alt="" />
            </div>
          </div>

          <div class="p-footer">
            <div class="p-author">
              <div class="p-av">{{ avatarText }}</div>
              <div class="p-name">{{ authStore.identity?.nickname || '匿名气泡' }}</div>
            </div>
            <div class="p-stats">
              <span>❤️ 0</span>
              <span>💬 0</span>
            </div>
          </div>
        </article>

        <p class="preview-hint">
          这是你的气泡在星空中的样子。左侧的修改会实时反映在这里。
        </p>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { postsApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'
import { getIdentityInitial, tagEmoji } from '../utils/presentation'

const router = useRouter()
const authStore = useAuthStore()

const DRAFT_KEY = 'anonymouswall-create-draft'
const FLASH_KEY = 'anonymouswall-flash'

const content = ref('')
const tag = ref('树洞')
const bgColor = ref(3)
const allowMessages = ref(true)
const destroyAfterHours = ref<number | null>(null)
const previewImages = ref<Array<string | null>>([null, null, null])
const imageFiles = ref<Array<File | null>>([null, null, null])
const pollEnabled = ref(false)
const pollQuestion = ref('')
const pollExpireDays = ref(3)
const pollOptions = ref(['', ''])
const loading = ref(false)
const notice = ref('')

const tagOptions = [
  { label: '表白', value: '表白', emoji: '💌' },
  { label: '吐槽', value: '吐槽', emoji: '😤' },
  { label: '求助', value: '求助', emoji: '🆘' },
  { label: '树洞', value: '树洞', emoji: '🕳️' },
  { label: '失物招领', value: '失物招领', emoji: '🔍' },
  { label: '搭子', value: '搭子', emoji: '🤝' },
]

const colorOptions = [
  { value: 1, className: 'bubble-1' },
  { value: 2, className: 'bubble-2' },
  { value: 3, className: 'bubble-3' },
  { value: 4, className: 'bubble-4' },
  { value: 5, className: 'bubble-5' },
  { value: 6, className: 'bubble-6' },
  { value: 7, className: 'bubble-7' },
  { value: 8, className: 'bubble-8' },
]

const destroyOptions = [
  { label: '24h', value: 24 },
  { label: '48h', value: 48 },
  { label: '7天', value: 24 * 7 },
  { label: '永久', value: null },
]

const avatarText = computed(() => getIdentityInitial(authStore.identity?.nickname || '星'))
const canPublish = computed(() => content.value.trim() && tag.value)
const currentTagLabel = computed(() => `${tagEmoji(tag.value)} ${tag.value}`)
const filledPreviewImages = computed(() => previewImages.value.filter(Boolean) as string[])

function showNotice(message: string) {
  notice.value = message
  window.setTimeout(() => {
    if (notice.value === message) notice.value = ''
  }, 2200)
}

function saveDraft() {
  localStorage.setItem(
    DRAFT_KEY,
    JSON.stringify({
      content: content.value,
      tag: tag.value,
      bgColor: bgColor.value,
      allowMessages: allowMessages.value,
      destroyAfterHours: destroyAfterHours.value,
    }),
  )
  showNotice('草稿已保存到本地')
}

async function refreshIdentity() {
  try {
    await authStore.refreshIdentity()
    showNotice('已切换匿名身份')
  } catch {
    showNotice('切换匿名身份失败，请稍后重试')
  }
}

function onSelectImage(event: Event, index: number) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  imageFiles.value[index] = file
  const reader = new FileReader()
  reader.onload = () => {
    previewImages.value[index] = String(reader.result)
  }
  reader.readAsDataURL(file)
}

function removeImage(index: number) {
  previewImages.value[index] = null
  imageFiles.value[index] = null
}

async function publish() {
  if (!canPublish.value) return
  loading.value = true
  notice.value = ''

  try {
    const formData = new FormData()
    formData.append('content', content.value.trim())
    formData.append('tag', tag.value)
    formData.append('bg_color', String(bgColor.value))
    formData.append('allow_messages', String(allowMessages.value))
    if (destroyAfterHours.value !== null) {
      formData.append('destroy_after_hours', String(destroyAfterHours.value))
    }
    imageFiles.value.filter(Boolean).forEach((file) => {
      formData.append('images', file as File)
    })
    if (pollEnabled.value) {
      formData.append('poll_enabled', 'true')
      formData.append('poll_question', pollQuestion.value.trim())
      formData.append('poll_expire_days', String(pollExpireDays.value))
      pollOptions.value.map((option) => option.trim()).filter(Boolean).forEach((option) => {
        formData.append('poll_options', option)
      })
    }

    const res = await postsApi.create(formData)
    localStorage.removeItem(DRAFT_KEY)
    sessionStorage.setItem(FLASH_KEY, res.data.message || '发布成功')
    const created = res.data.data
    if (created?.status === 'rejected') {
      router.push('/profile')
      return
    }
    router.push('/')
  } catch (error: any) {
    showNotice(error.response?.data?.message || '发布失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

const savedDraft = localStorage.getItem(DRAFT_KEY)
if (savedDraft) {
  try {
    const parsed = JSON.parse(savedDraft)
    content.value = parsed.content || ''
    tag.value = parsed.tag || '树洞'
    bgColor.value = parsed.bgColor || 3
    allowMessages.value = parsed.allowMessages ?? true
    destroyAfterHours.value = parsed.destroyAfterHours ?? null
  } catch {
    localStorage.removeItem(DRAFT_KEY)
  }
}
</script>

<style scoped>
.create-page {
  position: relative;
}

.page-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 18px;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 400px;
  min-height: calc(100vh - 180px);
  border-radius: 28px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.editor,
.preview {
  padding: 40px 32px 56px;
}

.editor {
  border-right: 1px solid rgba(255, 255, 255, 0.04);
}

.editor-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 32px;
  font-size: 1.375rem;
}

.field {
  margin-bottom: 28px;
}

.field-label {
  margin-bottom: 10px;
  color: var(--text-2);
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.field-label .req {
  color: var(--pink);
}

.field-label .sub {
  color: var(--text-3);
  font-weight: 400;
}

.identity-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
}

.id-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--gradient-brand);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
}

.id-name {
  font-size: 0.875rem;
  font-weight: 600;
}

.id-sub {
  color: var(--text-3);
  font-size: 0.6875rem;
}

.id-refresh {
  margin-left: auto;
  min-height: 32px;
  padding: 0 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-3);
}

.id-refresh:hover {
  color: var(--brand);
  border-color: rgba(124, 92, 252, 0.3);
}

textarea {
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
  color: var(--text-1);
  line-height: 1.8;
  resize: none;
  outline: none;
}

textarea::placeholder {
  color: var(--text-3);
}

textarea:focus {
  border-color: rgba(124, 92, 252, 0.4);
  box-shadow: 0 0 0 3px rgba(124, 92, 252, 0.08);
}

.count-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
}

.count-row span {
  color: var(--text-3);
  font-size: 0.75rem;
}

.count-row .warn {
  color: var(--pink);
}

.tags,
.colors,
.timer-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag,
.tc {
  min-height: 38px;
  padding: 0 16px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-2);
}

.tag.active,
.tc.active {
  background: var(--brand);
  border-color: var(--brand);
  color: #fff;
  box-shadow: 0 2px 12px rgba(124, 92, 252, 0.25);
}

.cdot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid transparent;
}

.cdot.active {
  border-color: #fff;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.15);
}

.img-row {
  display: flex;
  gap: 12px;
}

.img-box {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 16px;
  border: 2px dashed rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--text-3);
  overflow: hidden;
  cursor: pointer;
}

.img-box:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: rgba(124, 92, 252, 0.03);
}

.img-box.filled {
  border-style: solid;
}

.img-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.plus {
  font-size: 1.5rem;
  line-height: 1;
}

.rm {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 0;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
}

.tgl-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
}

.tgl-row + .tgl-row {
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.tgl-txt {
  color: var(--text-2);
  font-size: 0.8125rem;
}

.tgl {
  width: 40px;
  height: 22px;
  position: relative;
  border: 0;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.1);
}

.tgl::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.3s ease;
}

.tgl.on {
  background: var(--brand);
}

.tgl.on::after {
  transform: translateX(18px);
}

.notice {
  color: var(--pink);
  font-size: 0.8125rem;
}

.poll-builder {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.poll-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.poll-input,
.poll-select {
  min-height: 42px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-1);
}

.poll-builder-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.preview {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-title {
  margin-bottom: 24px;
  color: var(--text-2);
  font-size: 0.875rem;
  font-weight: 600;
}

.preview-bubble {
  width: 100%;
  max-width: 340px;
  padding: 22px;
  border-radius: 24px;
}

.p-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-2);
  font-size: 0.75rem;
  font-weight: 600;
}

.p-content {
  min-height: 44px;
  margin-bottom: 16px;
  color: var(--text-1);
  line-height: 1.7;
}

.p-content.placeholder {
  color: var(--text-3);
  font-style: italic;
}

.p-images {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.p-img {
  width: 60px;
  height: 60px;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.p-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.p-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.p-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.p-av {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--gradient-brand);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
}

.p-name {
  color: var(--text-2);
  font-size: 0.8125rem;
}

.p-stats {
  display: flex;
  gap: 12px;
  color: var(--text-3);
  font-size: 0.75rem;
}

.preview-hint {
  margin-top: 24px;
  max-width: 280px;
  text-align: center;
  color: var(--text-3);
  font-size: 0.75rem;
  line-height: 1.6;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .editor {
    border-right: 0;
  }

  .preview {
    display: none;
  }
}

@media (max-width: 640px) {
  .page-actions {
    justify-content: stretch;
  }

  .page-actions > * {
    flex: 1;
  }

  .editor {
    padding: 32px 16px 48px;
  }
}
</style>
