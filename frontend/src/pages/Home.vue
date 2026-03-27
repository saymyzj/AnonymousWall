<template>
  <div class="home">
    <section class="hero">
      <p class="eyebrow">Bubble Galaxy</p>
      <h1 class="hero-title">在星空中，发现你的气泡</h1>
      <p class="hero-sub">每一个匿名气泡，都是宇宙里一颗缓慢发光的星。</p>

      <form id="hero-search" class="hero-search" @submit.prevent="doHeroSearch">
        <span class="search-icon">🔍</span>
        <input
          v-model="heroSearchQuery"
          type="search"
          placeholder="搜索你感兴趣的话题..."
          aria-label="搜索帖子"
        />
        <button class="search-btn" type="submit">搜索</button>
      </form>
    </section>

    <section class="filter-area">
      <div class="tag-chips">
        <button
          v-for="tag in tags"
          :key="tag.label"
          class="chip"
          :class="{ active: filters.tag === tag.value }"
          type="button"
          @click="selectTag(tag.value)"
        >
          {{ tag.emoji }} {{ tag.label }}
        </button>
      </div>

      <div class="sort-pills">
        <button
          v-for="option in sortOptions"
          :key="option.value"
          class="pill"
          :class="{ active: activeSort === option.value }"
          type="button"
          @click="selectSort(option.value)"
        >
          {{ option.label }}
        </button>
      </div>
    </section>

    <div v-if="announcements.length" class="announcement-stack">
      <GlassCard
        v-for="announcement in announcements"
        :key="announcement.id"
        class="announcement-banner"
      >
        <div>
          <div class="announcement-title">系统公告 · {{ announcement.title }}</div>
          <div class="announcement-text">{{ announcement.content }}</div>
        </div>
        <button class="clear-link" type="button" @click="dismissAnnouncement(announcement.id)">关闭</button>
      </GlassCard>
    </div>

    <section v-if="pinnedPosts.length" class="pinned-section">
      <div class="section-heading">
        <h3>置顶气泡</h3>
        <span class="meta">管理员精选</span>
      </div>
      <div class="pinned-grid">
        <article v-for="post in pinnedPosts" :key="post.id" class="pinned-card bubble-surface" :class="`bubble-${post.bg_color}`" @click="goPinnedPost(post.id)">
          <div class="pin-tag">📌 置顶</div>
          <div class="pinned-content">{{ post.content_preview }}</div>
          <div class="pinned-footer">
            <span>{{ post.tag }}</span>
            <span>{{ post.comment_count }} 条评论</span>
          </div>
        </article>
      </div>
    </section>

    <GlassCard v-if="filters.search" class="search-hint">
      <div class="search-summary">
        <span class="summary-label">检索中</span>
        <strong>“{{ filters.search }}”</strong>
      </div>
      <button class="clear-link" type="button" @click="clearSearch">清除搜索</button>
    </GlassCard>

    <GlassCard v-if="flashMessage" class="search-hint flash-hint">
      <div class="search-summary">
        <span class="summary-label">提示</span>
        <strong>{{ flashMessage }}</strong>
      </div>
      <button class="clear-link" type="button" @click="flashMessage = ''">关闭</button>
    </GlassCard>

    <section v-if="postsStore.posts.length" class="masonry">
      <PostCard v-for="post in postsStore.posts" :key="post.id" :post="post" :search-term="filters.search" />
    </section>

    <div v-if="postsStore.loading" class="status-wrap">
      <GlassCard class="status-card">
        <div class="spinner"></div>
        <h3>正在汇聚新的气泡</h3>
        <p>列表正在从宇宙深处加载，请稍候。</p>
      </GlassCard>
    </div>

    <div v-else-if="!postsStore.posts.length" class="status-wrap">
      <GlassCard class="status-card empty-card">
        <h3>这里暂时还很安静</h3>
        <p>换个标签试试，或者发布第一条帖子点亮这片星空。</p>
      </GlassCard>
    </div>

    <div ref="loadMoreRef" class="load-trigger"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PostCard from '../components/PostCard.vue'
import GlassCard from '../components/GlassCard.vue'
import { postsApi } from '../api/posts'
import { usePostsStore } from '../stores/posts'

const router = useRouter()
const postsStore = usePostsStore()
const loadMoreRef = ref<HTMLElement>()
const heroSearchQuery = ref('')
const pinnedPosts = ref<any[]>([])
const announcements = ref<any[]>([])
const dismissedAnnouncementIds = ref<number[]>([])
const flashMessage = ref('')

const filters = computed(() => postsStore.filters)
const activeSort = computed(() => postsStore.filters.sort || 'latest')

const tags = [
  { label: '全部', value: undefined, emoji: '✨' },
  { label: '表白', value: '表白', emoji: '💌' },
  { label: '吐槽', value: '吐槽', emoji: '😤' },
  { label: '求助', value: '求助', emoji: '🆘' },
  { label: '树洞', value: '树洞', emoji: '🕳️' },
  { label: '失物招领', value: '失物招领', emoji: '🔍' },
  { label: '搭子', value: '搭子', emoji: '🤝' },
]

const sortOptions = [
  { label: '最新', value: 'latest' },
  { label: '最热', value: 'hot' },
  { label: '推荐', value: 'recommend' },
]

function doHeroSearch() {
  const query = heroSearchQuery.value.trim()
  postsStore.setFilter('search', query || undefined)
}

function selectTag(value?: string) {
  postsStore.setFilter('tag', value)
}

function selectSort(value: string) {
  postsStore.setFilter('sort', value)
}

function clearSearch() {
  heroSearchQuery.value = ''
  postsStore.setFilter('search', undefined)
}

function dismissAnnouncement(id: number) {
  dismissedAnnouncementIds.value.push(id)
  announcements.value = announcements.value.filter((item) => item.id !== id)
}

function goPinnedPost(id: number) {
  router.push(`/post/${id}`)
}

let observer: IntersectionObserver | null = null

watch(
  () => postsStore.filters.search,
  (value) => {
    heroSearchQuery.value = value || ''
  },
  { immediate: true },
)

onMounted(() => {
  const savedFlash = sessionStorage.getItem('anonymouswall-flash')
  if (savedFlash) {
    flashMessage.value = savedFlash
    sessionStorage.removeItem('anonymouswall-flash')
  }
  postsStore.resetState()
  postsStore.fetchPosts(true)
  postsApi.getHomeMeta().then((res) => {
    pinnedPosts.value = res.data.data.pinned_posts || []
    announcements.value = (res.data.data.announcements || []).filter(
      (item: any) => !dismissedAnnouncementIds.value.includes(item.id),
    )
  }).catch(() => undefined)

  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting && !postsStore.loading && postsStore.hasMore) {
        postsStore.fetchPosts()
      }
    },
    {
      rootMargin: '120px 0px',
      threshold: 0.1,
    },
  )

  if (loadMoreRef.value) {
    observer.observe(loadMoreRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero {
  padding: 60px 0 20px;
  text-align: center;
}

.eyebrow {
  margin: 0 0 14px;
  color: var(--pink);
  font-size: 0.75rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
}

.hero-title {
  margin: 0;
  font-size: 44px;
  line-height: 1.12;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.6));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-sub {
  width: min(620px, 100%);
  margin: 14px auto 0;
  color: var(--text-2);
  font-size: 1rem;
}

.hero-search {
  width: min(560px, 100%);
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 30px auto 0;
  padding: 6px 6px 6px 22px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: var(--shadow-soft);
}

.hero-search:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 4px rgba(124, 92, 252, 0.25);
}

.search-icon {
  opacity: 0.72;
}

.hero-search input {
  flex: 1;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text-1);
}

.hero-search input::placeholder {
  color: var(--text-3);
}

.search-btn {
  min-width: 92px;
  min-height: 44px;
  padding: 0 24px;
  border: 0;
  border-radius: var(--radius-pill);
  background: var(--brand);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 10px 24px rgba(124, 92, 252, 0.18);
}

.search-btn:hover {
  background: var(--brand-deep);
  box-shadow: 0 10px 24px rgba(124, 92, 252, 0.28);
}

.filter-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.announcement-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.announcement-banner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 18px;
}

.announcement-title {
  color: var(--text-1);
  font-size: 0.875rem;
  font-weight: 700;
}

.announcement-text {
  margin-top: 4px;
  color: var(--text-2);
  font-size: 0.875rem;
}

.pinned-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pinned-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.pinned-card {
  padding: 18px;
  border-radius: 22px;
  cursor: pointer;
}

.pin-tag {
  display: inline-flex;
  margin-bottom: 10px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.12);
  font-size: 0.75rem;
  font-weight: 600;
}

.pinned-content {
  color: var(--text-1);
  line-height: 1.6;
  margin-bottom: 12px;
}

.pinned-footer {
  display: flex;
  justify-content: space-between;
  color: var(--text-3);
  font-size: 0.75rem;
}

.tag-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip,
.pill {
  border-radius: var(--radius-pill);
  font-size: 0.875rem;
}

.chip {
  min-height: 40px;
  padding: 0 18px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-2);
}

.chip:hover {
  color: var(--brand);
  border-color: rgba(124, 92, 252, 0.3);
}

.chip.active {
  color: #fff;
  border-color: transparent;
  background: var(--brand);
  box-shadow: 0 2px 12px rgba(124, 92, 252, 0.25);
}

.sort-pills {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.pill {
  min-height: 36px;
  padding: 0 16px;
  border: 0;
  background: transparent;
  color: var(--text-3);
}

.pill:hover {
  color: var(--text-1);
}

.pill.active {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-1);
}

.search-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 18px;
}

.search-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-2);
}

.search-summary strong {
  color: var(--text-1);
}

.summary-label {
  color: var(--brand);
  font-size: 0.8125rem;
}

.clear-link {
  border: 0;
  background: transparent;
  color: var(--brand);
}

.masonry {
  columns: 4;
  column-gap: 20px;
}

.status-wrap {
  padding: 24px 0 12px;
}

.spinner {
  width: 32px;
  height: 32px;
  margin: 0 auto 16px;
  border: 3px solid rgba(255, 255, 255, 0.08);
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.empty-card {
  padding: 36px 28px;
}

.load-trigger {
  height: 1px;
}

@media (max-width: 1199px) {
  .masonry {
    columns: 3;
  }
}

@media (max-width: 899px) {
  .hero {
    padding-top: 40px;
  }

  .hero-title {
    font-size: 32px;
  }

  .masonry {
    columns: 2;
  }

  .pinned-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 599px) {
  .hero-search {
    padding-left: 16px;
  }

  .search-btn {
    min-width: 78px;
    padding: 0 18px;
  }

  .search-hint {
    flex-direction: column;
    align-items: flex-start;
  }

  .masonry {
    columns: 1;
  }
}
</style>
