import api from './index'

export const messagesApi = {
  getConversations() {
    return api.get('/messages/conversations/')
  },
  sendMessage(postId: number, content: string) {
    return api.post('/messages/send/', { post_id: postId, content })
  },
  replyMessage(conversationId: number, content: string) {
    return api.post(`/messages/conversations/${conversationId}/reply/`, { content })
  },
  blockConversation(conversationId: number) {
    return api.post(`/messages/conversations/${conversationId}/block/`)
  },
  getNotifications() {
    return api.get('/notifications/')
  },
  markAllRead() {
    return api.post('/notifications/read-all/')
  },
  ignoreNotification(id: number) {
    return api.post(`/notifications/${id}/ignore/`)
  },
}
