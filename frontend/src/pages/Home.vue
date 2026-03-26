<template>
  <div class="home">
    <!-- Tag Filter -->
    <div class="tag-bar">
      <button
        v-for="tag in tags"
        :key="tag.value"
        class="tag-btn"
        :class="{ active: filters.tag === tag.value }"
        @click="selectTag(tag.value)"
      >
        {{ tag.emoji }} {{ tag.label }}
      </button>
    </div>

    <!-- Sort Bar -->
    <div class="sort-bar">
      <div class="sort-options">
        <button
          v-for="s in sortOptions"
          :key="s.value"
          class="sort-btn"
          :class="{ active: filters.sort === s.value }"
          @click="postsStore.setFilter('sort', s.value)"
        >
          {{ s.label }}
        </button>
      </div>
      <select class="time-select" :value="filters.time || 'all'" @change="onTimeChange">
        <option value="all">全部时间</option>
        <option value="today">今天</option>
        <option value="week">本周</option>
        <option value="month">本月</option>
      </select>
    </div>

    <!-- Search Hint -->
    <div v-if="filters.search" class="search-hint">
      搜索 "{{ filters.search }}" 的结果
      <button @click="clearSearch">清除搜索</button>
    </div>

    <!-- Post Masonry Grid -->
    <div class="post-grid">
      <PostCard
        v-for="post in postsStore.posts"
        :key="post.id"
        :post="post"
      />
    </div>

    <!-- Loading -->
    <div v-if="postsStore.loading" class="status-area">
      <van-loading type="spinner" color="var(--brand-primary)" />
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
/* Tag Bar — centered */
.tag-bar {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  padding-bottom: 20px;
}

.tag-btn {
  padding: 8px 20px;
  border-radius: 999px;
  border: 1.5px solid var(--divider);
  background: white;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-btn:hover:not(.active) {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
  background: var(--brand-primary-light);
  transform: translateY(-1px);
}

.tag-btn.active {
  background: var(--brand-primary);
  color: white;
  border-color: var(--brand-primary);
  box-shadow: 0 2px 8px rgba(124, 92, 252, 0.25);
  animation: tag-pop 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes tag-pop {
  0% { transform: scale(1); }
  50% { transform: scale(1.08); }
  100% { transform: scale(1); }
}

/* Sort Bar */
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0 20px;
}

.sort-options {
  display: flex;
  gap: 20px;
}

.sort-btn {
  background: none;
  border: none;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.sort-btn:hover {
  color: var(--brand-primary);
  transform: none;
}

.sort-btn.active {
  color: var(--brand-primary);
  border-bottom-color: var(--brand-primary);
  font-weight: 600;
}

.time-select {
  background: white;
  border: 1.5px solid var(--divider);
  border-radius: 999px;
  padding: 6px 16px;
  font-size: 13px;
  color: var(--text-secondary);
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.time-select:hover {
  border-color: var(--brand-primary);
}

/* Search Hint */
.search-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  margin-bottom: 20px;
  background: var(--brand-primary-light);
  border-radius: 12px;
  font-size: 14px;
  color: var(--brand-primary);
}

.search-hint button {
  background: none;
  border: none;
  color: var(--brand-primary);
  font-size: 13px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: underline;
}

/* Masonry Grid */
.post-grid {
  column-count: 2;
  column-gap: 28px;
}

.post-grid > :deep(*) {
  break-inside: avoid;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .post-grid {
    column-count: 3;
  }
}

@media (min-width: 1024px) {
  .post-grid {
    column-count: 4;
  }
}

@media (min-width: 1400px) {
  .post-grid {
    column-count: 5;
  }
}

/* Status / Loading / Empty */
.status-area {
  text-align: center;
  padding: 48px 0;
  color: var(--text-secondary);
}

.empty-text {
  font-size: 16px;
  color: var(--text-placeholder);
}

.load-trigger {
  height: 1px;
}
</style>
