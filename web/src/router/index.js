import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/process',
    name: 'Process',
    component: () => import('../views/Process.vue')
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: () => import('../views/Jobs.vue')
  },
  {
    path: '/jobs/:id',
    name: 'JobDetail',
    component: () => import('../views/JobDetail.vue')
  },
  {
    path: '/validate',
    name: 'Validate',
    component: () => import('../views/Validate.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
