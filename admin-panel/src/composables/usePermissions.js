import { computed } from 'vue'
import { useAuthStore } from '../store/auth'
import { useRolesStore } from '../store/roles'

export function usePermissions() {
  const authStore = useAuthStore()
  const rolesStore = useRolesStore()

  // Información del usuario actual
  const currentUser = computed(() => authStore.user)
  const currentUserRole = computed(() => currentUser.value?.role_id)

  // Funciones de verificación de permisos
  const hasPermission = (permission, action = null) => {
    try {
      if (!currentUserRole.value) return false
      if (!rolesStore.roles || rolesStore.roles.length === 0) return false
      return rolesStore.hasPermission(currentUserRole.value, permission, action)
    } catch (error) {
      // Solo loguear errores críticos
      if (error.message !== 'Network Error') {
        console.warn('Permission check failed:', permission, action)
      }
      return false
    }
  }

  const hasAnyPermission = (permissions) => {
    try {
      if (!currentUserRole.value) return false
      if (!rolesStore.roles || rolesStore.roles.length === 0) return false
      return rolesStore.hasAnyPermission(currentUserRole.value, permissions)
    } catch (error) {
      return false
    }
  }

  // Permisos específicos por módulo
  const permissions = {
    // Dashboard
    dashboard: {
      view: () => {
        try {
          return hasPermission('dashboard', 'read')
        } catch (error) {
          return true // Fallback: permitir dashboard por defecto
        }
      }
    },

    // Companies
    companies: {
      view: () => {
        try {
          return hasPermission('companies', 'read')
        } catch (error) {
          console.error('Error checking companies view permission:', error)
          return false
        }
      },
      create: () => {
        try {
          return hasPermission('companies', 'create')
        } catch (error) {
          console.error('Error checking companies create permission:', error)
          return false
        }
      },
      update: () => {
        try {
          return hasPermission('companies', 'update')
        } catch (error) {
          console.error('Error checking companies update permission:', error)
          return false
        }
      },
      delete: () => {
        try {
          return hasPermission('companies', 'delete')
        } catch (error) {
          console.error('Error checking companies delete permission:', error)
          return false
        }
      }
    },

    // Warehouses
    warehouses: {
      view: () => {
        try {
          return hasPermission('warehouses', 'read')
        } catch (error) {
          console.error('Error checking warehouses view permission:', error)
          return false
        }
      },
      create: () => {
        try {
          return hasPermission('warehouses', 'create')
        } catch (error) {
          console.error('Error checking warehouses create permission:', error)
          return false
        }
      },
      update: () => {
        try {
          return hasPermission('warehouses', 'update')
        } catch (error) {
          console.error('Error checking warehouses update permission:', error)
          return false
        }
      },
      delete: () => {
        try {
          return hasPermission('warehouses', 'delete')
        } catch (error) {
          console.error('Error checking warehouses delete permission:', error)
          return false
        }
      }
    },

    // Employees
    employees: {
      view: () => {
        try {
          return hasPermission('employees', 'read')
        } catch (error) {
          console.error('Error checking employees view permission:', error)
          return false
        }
      },
      create: () => {
        try {
          return hasPermission('employees', 'create')
        } catch (error) {
          console.error('Error checking employees create permission:', error)
          return false
        }
      },
      update: () => {
        try {
          return hasPermission('employees', 'update')
        } catch (error) {
          console.error('Error checking employees update permission:', error)
          return false
        }
      },
      delete: () => {
        try {
          return hasPermission('employees', 'delete')
        } catch (error) {
          console.error('Error checking employees delete permission:', error)
          return false
        }
      },
      registerFace: () => {
        try {
          return hasPermission('employees', 'register_face')
        } catch (error) {
          console.error('Error checking employees register face permission:', error)
          return false
        }
      }
    },

    // Users
    users: {
      view: () => {
        try {
          return hasPermission('users', 'read')
        } catch (error) {
          console.error('Error checking users view permission:', error)
          return false
        }
      },
      create: () => {
        try {
          return hasPermission('users', 'create')
        } catch (error) {
          console.error('Error checking users create permission:', error)
          return false
        }
      },
      update: () => {
        try {
          return hasPermission('users', 'update')
        } catch (error) {
          console.error('Error checking users update permission:', error)
          return false
        }
      },
      delete: () => {
        try {
          return hasPermission('users', 'delete')
        } catch (error) {
          console.error('Error checking users delete permission:', error)
          return false
        }
      }
    },

    // Roles
    roles: {
      view: () => {
        try {
          return hasPermission('roles', 'read')
        } catch (error) {
          console.error('Error checking roles view permission:', error)
          return false
        }
      }
      // No create, update, delete ya que los roles son solo lectura
    },

    // Logs
    logs: {
      view: () => {
        try {
          return hasPermission('logs', 'read')
        } catch (error) {
          console.error('Error checking logs view permission:', error)
          return false
        }
      },
      export: () => {
        try {
          return hasPermission('logs', 'export')
        } catch (error) {
          console.error('Error checking logs export permission:', error)
          return false
        }
      }
    },

    // Reports
    reports: {
      view: () => {
        try {
          return hasPermission('reports', 'read')
        } catch (error) {
          console.error('Error checking reports view permission:', error)
          return false
        }
      },
      generate: () => {
        try {
          return hasPermission('reports', 'generate')
        } catch (error) {
          console.error('Error checking reports generate permission:', error)
          return false
        }
      },
      export: () => {
        try {
          return hasPermission('reports', 'export')
        } catch (error) {
          console.error('Error checking reports export permission:', error)
          return false
        }
      }
    }
  }

  // Verificar acceso a rutas
  const canAccessRoute = (routeName) => {
    try {
      if (!currentUserRole.value) return false
      
      const routePermissions = {
        'Dashboard': permissions.dashboard.view(),
        'Companies': permissions.companies.view(),
        'Warehouses': permissions.warehouses.view(),
        'Employees': permissions.employees.view(),
        'Users': permissions.users.view(),
        'Roles': permissions.roles.view(),
        'Logs': permissions.logs.view(),
        'Reports': permissions.reports.view()
      }

      return routePermissions[routeName] || false
    } catch (error) {
      console.error('Error checking route access for', routeName, error)
      // Fallback: permitir solo dashboard para evitar errores
      return routeName === 'Dashboard'
    }
  }

  // Obtener rutas disponibles para el usuario
  const availableRoutes = computed(() => {
    try {
      const routes = [
        { name: 'Dashboard', path: '/admin/dashboard', icon: '📊' },
        { name: 'Companies', path: '/admin/companies', icon: '🏢' },
        { name: 'Warehouses', path: '/admin/warehouses', icon: '🏭' },
        { name: 'Employees', path: '/admin/employees', icon: '👥' },
        { name: 'Users', path: '/admin/users', icon: '👤' },
        { name: 'Roles', path: '/admin/roles', icon: '🔑' },
        { name: 'Logs', path: '/admin/logs', icon: '📋' },
        { name: 'Reports', path: '/admin/reports', icon: '📈' }
      ]

      if (!currentUserRole.value || !rolesStore.roles || rolesStore.roles.length === 0) {
        // Si no hay usuario o roles, solo mostrar Dashboard
        return [{ name: 'Dashboard', path: '/admin/dashboard', icon: '📊' }]
      }

      const filteredRoutes = routes.filter(route => {
        try {
          return route && route.name && canAccessRoute(route.name)
        } catch (error) {
          console.error('Error filtering route:', route, error)
          return false
        }
      })
      
      // Asegurar que siempre haya al menos Dashboard disponible
      if (filteredRoutes.length === 0) {
        return [{ name: 'Dashboard', path: '/admin/dashboard', icon: '📊' }]
      }

      return filteredRoutes
    } catch (error) {
      console.error('Error getting available routes:', error)
      return [{ name: 'Dashboard', path: '/admin/dashboard', icon: '📊' }]
    }
  })

  // Verificar si es administrador
  const isAdmin = computed(() => {
    const role = rolesStore.getRoleById(currentUserRole.value)
    return role?.name?.toLowerCase() === 'admin' || role?.name?.toLowerCase() === 'administrator'
  })

  return {
    // Estados
    currentUser,
    currentUserRole,
    isAdmin,

    // Funciones principales
    hasPermission,
    hasAnyPermission,
    canAccessRoute,

    // Permisos por módulo
    permissions,

    // Rutas disponibles
    availableRoutes,

    // Store references (por si se necesitan)
    rolesStore
  }
}