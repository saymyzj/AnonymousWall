import api from './index'

export interface PostParams {
  tag?: string
  time?: string
  sort?: string
  search?: string
  page?: number
}

export const postsApi = {
  getList(params: PostParams = {}) {
    return api.get('/posts/', { params })
  },
  getHomeMeta() {
    return api.get('/home/meta/')
  },
  getDetail(id: number) {
    return api.get(`/posts/${id}/`)
  },
  create(data: FormData) {
    return api.post('/posts/create/', data)
  },
  update(id: number, data: FormData) {
    return api.patch(`/posts/${id}/edit/`, data)
  },
  vote(id: number, optionId: number) {
    return api.post(`/posts/${id}/vote/`, { option_id: optionId })
  },
  delete(id: number) {
    return api.delete(`/posts/${id}/delete/`)
  },
  toggleLike(id: number) {
    return api.post(`/posts/${id}/like/`)
  },
  toggleFavorite(id: number) {
    return api.post(`/posts/${id}/favorite/`)
  },
  report(data: { target_type: 'post' | 'comment'; target_id: number; reason: string; detail?: string }) {
    return api.post('/reports/create/', data)
  },
}
