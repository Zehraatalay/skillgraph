import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'

import RepositoryMatchingView from "../views/RepositoryMatchingView.vue";
import DeveloperMatchingView from "../views/DeveloperMatchingView.vue";
import SkillAnalysisView from '@/views/SkillAnalysisView.vue'
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
    {
      path: "/developer-matching",
      name: "developer-matching",
      component: DeveloperMatchingView,
    },
    {
      path: '/skill-analysis',
      name: 'skill-analysis',
      component: SkillAnalysisView,
    },
  ],
})

export default router
