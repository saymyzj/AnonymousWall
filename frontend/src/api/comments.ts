import api from './index'

export const commentsApi = {
  getList(postId: number, params: { page?: number } = {}) {
    return api.get(`/posts/${postId}/comments/`, { params })
  },
  create(postId: number, data: { content: string; parent_id?: number | null }) {
    return api.post(`/posts/${postId}/comments/create/`, data)
  },
  delete(id: number) {
    return api.delete(`/comments/${id}/delete/`)
  },
  toggleLike(id: number) {
    return api.post(`/comments/${id}/like/`)
  },
}
