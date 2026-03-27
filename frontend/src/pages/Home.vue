<template>
  <div class="home">
    <!-- Hero Search Area -->
    <div class="hero">
      <h1 class="hero-title">在星空中，发现你的气泡</h1>
      <p class="hero-sub">每一个匿名气泡，都是宇宙中独特的星光</p>
      <div class="hero-search" id="hero-search">
        <span class="search-icon">🔍</span>
        <input
          v-model="heroSearchQuery"
          placeholder="搜索你感兴趣的话题..."
          @keyup.enter="doHeroSearch"
        />
        <button class="search-btn" @click="doHeroSearch">搜索</button>
      </div>
    </div>

    <!-- Filter Area -->
    <div class="filter-area">
      <div class="tag-chips">
        <button
          v-for="tag in tags"
          :key="tag.value"
          class="chip"
          :class="{ active: filters.tag === tag.value }"
          @click="selectTag(tag.value)"
        >
          {{ tag.emoji }} {{ tag.label }}
        </button>
      </div>
      <div class="sort-pills">
        <button
          v-for="s in sortOptions"
          :key="s.value"
          class="pill"
          :class="{ active: filters.sort === s.value }"
          @click="postsStore.setFilter('sort', s.value)"
        >
          {{ s.label }}
        </button>
      </div>
    </div>

    <!-- Search Hint -->
    <div v-if="filters.search" class="search-hint">
      搜索 "{{ filters.search }}" 的结果
      <button @click="clearSearch">清除搜索</button>
    </div>

    <!-- Masonry Grid -->
    <div class="masonry">
      <PostCard
        v-for="post in postsStore.posts"
        :key="post.id"
        :post="post"
      />
    </div>

    <!-- Loading -->
    <div v-if="postsStore.loading" class="status-area">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Empty -->
    <div v-if="!postsStore.loading && postsStore.posts.length === 0" class="status-area">
      <p class="empty-text">还没有内容，快来发第一条帖子吧</p>
    </div>

    <!-- Load More Trigger -->
    <div ref="loadMoreRef" class="load-trigger"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { usePostsStore } from '../stores/posts'
import PostCard from '../components/PostCard.vue'

const postsStore = usePostsStore()
const loadMoreRef = ref<HTMLElement>()
const filters = computed(() => postsStore.filters)

const heroSearchQuery = ref('')

function doHeroSearch() {
  const q = heroSearchQuery.value.trim()
  if (q) {
    postsStore.setFilter('search', q)
  }
}

const tags = [
  { label: '全部', value: undefined, emoji: '' },
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
]

function selectTag(value: string | undefined) {
  postsStore.setFilter('tag', value)
}

function onTimeChange(e: Event) {
  const val = (e.target as HTMLSelectElement).value
  postsStore.setFilter('time', val === 'all' ? undefined : val)
}

function clearSearch() {
  postsStore.setFilter('search', undefined)
}

let observer: IntersectionObserver | null = null

onMounted(() => {
  postsStore.fetchPosts(true)

  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && !postsStore.loading && postsStore.hasMore) {
        postsStore.fetchPosts()
      }
    },
    { threshold: 0.1 }
  )
  if (loadMoreRef.value) observer.observe(loadMoreRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
/* Hero Section */
.hero {
  text-align: center;
  padding-top: 60px;
  padding-bottom: 40px;
}

.hero-title {
  font-size: 44px;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.6));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.hero-sub {
  font-size: 16px;
  color: var(--text-2);
  margin-top: 12px;
}

.hero-search {
  max-width: 560px;
  margin: 28px auto 0;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  padding: 6px 6px 6px 20px;
  gap: 8px;
  transition: all 0.3s ease;
}

.hero-search:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 4px rgba(124, 92, 252, 0.25);
}

.search-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.hero-search input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-1);
  font-size: 15px;
  outline: none;
}

.hero-search input::placeholder {
  color: var(--text-3);
}

.search-btn {
  padding: 10px 24px;
  border-radius: 999px;
  background: var(--brand);
  color: white;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: box-shadow 0.3s ease;
  flex-shrink: 0;
}

.search-btn:hover {
  box-shadow: 0 4px 20px rgba(124, 92, 252, 0.25);
}

/* Filter Area */
.filter-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.tag-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  padding: 8px 20px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-2);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip:hover:not(.active) {
  border-color: var(--brand);
  color: var(--brand);
}

.chip.active {
  background: var(--brand);
  color: white;
  border-color: var(--brand);
  box-shadow: 0 2px 12px rgba(124, 92, 252, 0.25);
}

.sort-pills {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 999px;
  padding: 4px;
}

.pill {
  padding: 6px 16px;
  border-radius: 999px;
  border: none;
  background: transparent;
  color: var(--text-2);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill.active {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-1);
}

/* Search Hint */
.search-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  margin-bottom: 20px;
  background: rgba(124, 92, 252, 0.1);
  border: 1px solid rgba(124, 92, 252, 0.2);
  border-radius: 12px;
  font-size: 14px;
  color: var(--brand);
}

.search-hint button {
  background: none;
  border: none;
  color: var(--brand);
  font-size: 13px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: underline;
}

/* Masonry Grid */
.masonry {
  column-count: 4;
  column-gap: 20px;
}

@media (max-width: 1199px) {
  .masonry {
    column-count: 3;
  }
}

@media (max-width: 899px) {
  .masonry {
    column-count: 2;
  }
  .hero-title {
    font-size: 32px;
  }
}

@media (max-width: 599px) {
  .masonry {
    column-count: 1;
  }
}

/* Status / Loading / Empty */
.status-area {
  text-align: center;
  padding: 48px 0;
  color: var(--text-2);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-text {
  font-size: 16px;
  color: var(--text-3);
}

.load-trigger {
  height: 1px;
}
</style>
