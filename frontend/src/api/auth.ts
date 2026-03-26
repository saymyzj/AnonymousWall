import api from './index'

export const authApi = {
  register(data: { email: string; password: string; student_id: string; real_name: string }) {
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
}
