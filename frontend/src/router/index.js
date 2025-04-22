import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue')
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('@/views/UploadPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/materials',
    name: 'Materials',
    component: () => import('@/views/MaterialsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/materials/:id',
    name: 'MaterialDetail',
    component: () => import('@/views/MaterialDetailPage.vue')
  },
  {
    path: '/accounts',
    name: 'Accounts',
    component: () => import('@/views/AccountsPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterPage.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } 
  // Check if route requires admin privileges
  else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next({ name: 'Home' })
  }
  else {
    next()
  }
})

export default router 