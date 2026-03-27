import { defineStore } from 'pinia'
import { ref } from 'vue'
import { postsApi, type PostParams } from '../api/posts'

export const usePostsStore = defineStore('posts', () => {
  const posts = ref<any[]>([])
  const loading = ref(false)
  const hasMore = ref(true)
  const currentPage = ref(1)
  const requestId = ref(0)
  const filters = ref<PostParams>({
    tag: undefined,
    time: undefined,
    sort: 'latest',
    search: undefined,
  })

  function resetState() {
    posts.value = []
    loading.value = false
    hasMore.value = true
    currentPage.value = 1
    requestId.value += 1
  }

  async function fetchPosts(reset = false) {
    if (loading.value) return
    if (!reset && !hasMore.value) return

    if (reset) {
      requestId.value += 1
      currentPage.value = 1
      hasMore.value = true
    }

    const currentRequest = requestId.value
    loading.value = true
    try {
      const res = await postsApi.getList({
        ...filters.value,
        page: currentPage.value,
      })
      if (currentRequest !== requestId.value) return
      const results = res.data.results || []
      if (reset) {
        posts.value = results
      } else {
        posts.value.push(...results)
      }
      hasMore.value = !!res.data.next
      currentPage.value++
    } finally {
      loading.value = false
    }
  }

  function setFilter(key: keyof PostParams, value: any) {
    filters.value[key] = value
    fetchPosts(true)
  }

  return { posts, loading, hasMore, filters, fetchPosts, setFilter, resetState }
})
