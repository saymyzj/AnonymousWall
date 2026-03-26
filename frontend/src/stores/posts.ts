import { defineStore } from 'pinia'
import { ref } from 'vue'
import { postsApi, type PostParams } from '../api/posts'

export const usePostsStore = defineStore('posts', () => {
  const posts = ref<any[]>([])
  const loading = ref(false)
  const hasMore = ref(true)
  const currentPage = ref(1)
  const filters = ref<PostParams>({
    tag: undefined,
    time: undefined,
    sort: 'latest',
  })

  async function fetchPosts(reset = false) {
    if (loading.value) return
    if (!reset && !hasMore.value) return

    if (reset) {
      currentPage.value = 1
      hasMore.value = true
    }

    loading.value = true
    try {
      const res = await postsApi.getList({
        ...filters.value,
        page: currentPage.value,
      })
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

  return { posts, loading, hasMore, filters, fetchPosts, setFilter }
})
