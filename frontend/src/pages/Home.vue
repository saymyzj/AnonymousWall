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

    <!-- Post List -->
    <div class="post-list">
      <PostCard
        v-for="post in postsStore.posts"
        :key="post.id"
        :post="post"
      />
    </div>

    <!-- Loading -->
    <div v-if="postsStore.loading" class="loading">
      <van-loading type="spinner" color="var(--brand-primary)" />
    </div>

    <!-- Empty -->
    <div v-if="!postsStore.loading && postsStore.posts.length === 0" class="empty">
      <p>还没有内容，快来发第一条帖子吧 ✨</p>
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
.tag-bar {
  display: flex;
  gap: var(--space-2);
  overflow-x: auto;
  padding-bottom: var(--space-3);
  -webkit-overflow-scrolling: touch;
}

.tag-btn {
  flex-shrink: 0;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--divider);
  background: var(--card-bg);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-btn.active {
  background: var(--brand-primary);
  color: white;
  border-color: var(--brand-primary);
}

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
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.loading, .empty {
  text-align: center;
  padding: var(--space-8) 0;
  color: var(--text-secondary);
}

.empty p {
  font-size: 15px;
}

.load-trigger {
  height: 1px;
}

@media (min-width: 768px) {
  .post-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }
}
</style>
