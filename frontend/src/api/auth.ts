import api from './index'

export const authApi = {
  register(data: { email: string; password: string; student_id: string; real_name?: string }) {
    return api.post('/auth/register/', data)
  },
  login(email: string, password: string) {
    return api.post('/auth/login/', { email, password })
  },
  refreshToken(refresh: string) {
    return api.post('/auth/token/refresh/', { refresh })
  },
  getMe() {
    return api.get('/auth/me/')
  },
  updatePreferences(data: { theme_preference?: string; real_name?: string; student_id?: string }) {
    return api.patch('/auth/preferences/', data)
  },
  getDashboard() {
    return api.get('/auth/dashboard/')
  },
  refreshIdentity() {
    return api.post('/auth/identities/refresh/')
  },
}
