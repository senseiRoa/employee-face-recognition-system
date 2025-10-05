import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// Importar las vistas
import Dashboard from '@/views/Dashboard.vue'
import Login from '@/views/Login.vue'
import Companies from '@/views/Companies.vue'
import Warehouses from '@/views/Warehouses.vue'
import Employees from '@/views/Employees.vue'
import Users from '@/views/Users.vue'
import Roles from '@/views/Roles.vue'
import Logs from '@/views/Logs.vue'
import Reports from '@/views/Reports.vue'
import Layout from '@/components/Layout.vue'

const routes = [
  {
    path: '/admin/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'companies',
        name: 'Companies',
        component: Companies
      },
      {
        path: 'warehouses',
        name: 'Warehouses',
        component: Warehouses
      },
      {
        path: 'employees',
        name: 'Employees',
        component: Employees
      },
      {
        path: 'users',
        name: 'Users',
        component: Users
      },
      {
        path: 'roles',
        name: 'Roles',
        component: Roles
      },
      {
        path: 'logs',
        name: 'Logs',
        component: Logs
      },
      {
        path: 'reports',
        name: 'Reports',
        component: Reports
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/admin/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard de autenticación
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    next('/admin/login')
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next('/admin/dashboard')
  } else {
    next()
  }
})

export default router