import api from './index'

export const authApi = {
  register(email: string, password: string) {
    return api.post('/auth/register/', { email, password })
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
