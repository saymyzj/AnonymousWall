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
      搜索"{{ filters.search }}"的结果
      <button @click="clearSearch">清除</button>
    </div>

    <!-- Post List -->
    <div class="post-list">
      <PostCard
        v-for="(post, index) in postsStore.posts"
        :key="post.id"
        :post="post"
        :style="cardStyle(index)"
      />
    </div>

    <!-- Loading -->
    <div v-if="postsStore.loading" class="loading">
      <van-loading type="spinner" color="var(--brand-primary)" />
    </div>

    <!-- Empty -->
    <div v-if="!postsStore.loading && postsStore.posts.length === 0" class="empty">
      <p>还没有内容，快来发第一条帖子吧</p>
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

// Micro-rotation offsets for bubble feel
function cardStyle(index: number) {
  const rotations = [0.3, -0.5, 0.2, -0.3, 0.5, -0.2, 0.4, -0.4]
  const rot = rotations[index % rotations.length]
  return { '--card-rotation': `${rot}deg` }
}

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
/* Tag Filter Bar — centered on PC */
.tag-bar {
  display: flex;
  gap: var(--space-2);
  padding-bottom: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
}

.tag-btn {
  flex-shrink: 0;
  padding: 8px 18px;
  border-radius: 999px;
  border: 1px solid var(--divider);
  background: var(--card-bg);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-btn:hover:not(.active) {
  background: var(--brand-primary-light);
  border-color: var(--brand-primary);
  color: var(--brand-primary);
  transform: translateY(-1px);
}

.tag-btn.active {
  background: var(--brand-primary);
  color: white;
  border-color: var(--brand-primary);
  animation: tag-bounce 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes tag-bounce {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* Sort Bar */
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) 0 var(--space-3);
}

.sort-options {
  display: flex;
  gap: var(--space-4);
}

.sort-btn {
  background: none;
  border: none;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}

.sort-btn:hover {
  color: var(--brand-primary);
}

.sort-btn.active {
  color: var(--brand-primary);
  border-bottom-color: var(--brand-primary);
  font-weight: 600;
}

.time-select {
  background: var(--card-bg);
  border: 1px solid var(--divider);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  color: var(--text-secondary);
  outline: none;
  cursor: pointer;
}

.time-select:hover {
  border-color: var(--brand-primary);
}

/* Post List — 3-column masonry on desktop */
.post-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.loading, .empty {
  text-align: center;
  padding: var(--space-8) 0;
  color: var(--text-secondary);
}

.empty p {
  font-size: 15px;
}

.search-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-3);
  background: var(--brand-primary-light);
  border-radius: 12px;
  font-size: 13px;
  color: var(--brand-primary);
}

.search-hint button {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
}

.load-trigger {
  height: 1px;
}

/* Tablet: 2-column masonry */
@media (min-width: 768px) {
  .post-list {
    display: block;
    column-count: 2;
    column-gap: 20px;
  }

  .post-list > :deep(*) {
    break-inside: avoid;
    margin-bottom: 16px;
  }
}

/* Desktop: 3-column masonry */
@media (min-width: 1024px) {
  .post-list {
    column-count: 3;
    column-gap: 24px;
  }

  .post-list > :deep(*) {
    margin-bottom: 20px;
  }
}
</style>
