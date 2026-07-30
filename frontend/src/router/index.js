import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'

import RepositoryMatchingView from "../views/RepositoryMatchingView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: "/repository-matching",
      name: "repository-matching",
      component: RepositoryMatchingView,
    },
  ],
})

export default router
