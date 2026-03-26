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
  getDetail(id: number) {
    return api.get(`/posts/${id}/`)
  },
  create(data: { content: string; tag: string; bg_color: number }) {
    return api.post('/posts/create/', data)
  },
  delete(id: number) {
    return api.delete(`/posts/${id}/delete/`)
  },
  toggleLike(id: number) {
    return api.post(`/posts/${id}/like/`)
  },
}
