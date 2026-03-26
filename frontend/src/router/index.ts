import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../layouts/DefaultLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('../pages/Home.vue') },
      { path: 'post/:id', name: 'PostDetail', component: () => import('../pages/PostDetail.vue') },
      { path: 'create', name: 'CreatePost', component: () => import('../pages/CreatePost.vue'), meta: { requiresAuth: true } },
      { path: 'profile', name: 'Profile', component: () => import('../pages/Profile.vue'), meta: { requiresAuth: true } },
    ],
  },
  { path: '/login', name: 'Login', component: () => import('../pages/Login.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
