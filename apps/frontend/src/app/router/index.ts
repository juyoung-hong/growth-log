import { createRouter, createWebHistory } from 'vue-router'

/**
 * 페이지는 지연 로딩한다. 지금은 화면이 작아 차이가 없지만, 달력·칸반처럼
 * 무거운 화면이 붙어도 첫 진입이 느려지지 않게 처음부터 이 형태로 둔다.
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 개인/회사는 별도 라우트가 아니라 쿼리 파라미터다.
    { path: '/', redirect: { path: '/task-groups', query: { scope: 'company' } } },
    {
      path: '/task-groups',
      name: 'task-groups',
      component: () => import('@/pages/task-groups').then(m => m.TaskGroupsPage),
    },
    {
      path: '/task-groups/:id',
      name: 'task-group-detail',
      component: () => import('@/pages/task-group-detail').then(m => m.TaskGroupDetailPage),
    },
    {
      path: '/task-groups/:id/tasks/:taskId',
      name: 'task-detail',
      component: () => import('@/pages/task-detail').then(m => m.TaskDetailPage),
    },
    {
      path: '/persons',
      name: 'persons',
      component: () => import('@/pages/persons').then(m => m.PersonsPage),
    },
    {
      path: '/storage',
      name: 'storage',
      component: () => import('@/pages/storage').then(m => m.StoragePage),
    },
  ],
})

export default router