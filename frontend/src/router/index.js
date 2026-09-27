import { createRouter, createWebHistory } from 'vue-router'
import Welcome from '../components/pages/Welcome.vue'
import Chat from '../components/pages/Chat.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Welcome,
    },
    {
      path: '/chat',
      name: 'chat',
      component: Chat,
    },
  ],
})

export default router
