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
      if (!currentUserRole.value) {
        return false
      }
      if (!rolesStore.roles || rolesStore.roles.length === 0) {
        return false
      }
      
      const result = rolesStore.hasPermission(currentUserRole.value, permission, action)
      return result
    } catch (error) {
      console.warn('Permission check failed:', permission, action, error)
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
          const result = hasPermission('dashboard', 'read')
          return result || true // Fallback: permitir dashboard por defecto
        } catch (error) {
          return true // Fallback: permitir dashboard por defecto
        }
      }
    },

    // Companies
    companies: {
      view: () => {
        try {
          // Usar tanto 'companies' como 'company_management' 
          return hasPermission('companies', 'read') || hasPermission('company_management', 'read')
        } catch (error) {
          console.error('Error checking companies view permission:', error)
          return false
        }
      },
      create: () => {
        try {
          return hasPermission('companies', 'create') || hasPermission('company_management', 'write')
        } catch (error) {
          console.error('Error checking companies create permission:', error)
          return false
        }
      },
      update: () => {
        try {
          return hasPermission('companies', 'update') || hasPermission('company_management', 'write')
        } catch (error) {
          console.error('Error checking companies update permission:', error)
          return false
        }
      },
      delete: () => {
        try {
          return hasPermission('companies', 'delete') || hasPermission('company_management', 'delete')
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
          return hasPermission('warehouses', 'read') || hasPermission('warehouse_access', 'read')
        } catch (error) {
          console.error('Error checking warehouses view permission:', error)
          return false
        }
      },
      create: () => {
        try {
          return hasPermission('warehouses', 'create') || hasPermission('warehouse_access', 'write')
        } catch (error) {
          console.error('Error checking warehouses create permission:', error)
          return false
        }
      },
      update: () => {
        try {
          return hasPermission('warehouses', 'update') || hasPermission('warehouse_access', 'write')
        } catch (error) {
          console.error('Error checking warehouses update permission:', error)
          return false
        }
      },
      delete: () => {
        try {
          return hasPermission('warehouses', 'delete') || hasPermission('warehouse_access', 'delete')
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
          return hasPermission('employees', 'read') || hasPermission('employee_management', 'read')
        } catch (error) {
          console.error('Error checking employees view permission:', error)
          return false
        }
      },
      create: () => {
        try {
          return hasPermission('employees', 'create') || hasPermission('employee_management', 'write')
        } catch (error) {
          console.error('Error checking employees create permission:', error)
          return false
        }
      },
      update: () => {
        try {
          return hasPermission('employees', 'update') || hasPermission('employee_management', 'write')
        } catch (error) {
          console.error('Error checking employees update permission:', error)
          return false
        }
      },
      delete: () => {
        try {
          return hasPermission('employees', 'delete') || hasPermission('employee_management', 'delete')
        } catch (error) {
          console.error('Error checking employees delete permission:', error)
          return false
        }
      },
      registerFace: () => {
        try {
          return hasPermission('employees', 'register_face') || hasPermission('employee_management', 'write')
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
          return hasPermission('users', 'read') || hasPermission('user_management', 'read')
        } catch (error) {
          console.error('Error checking users view permission:', error)
          return false
        }
      },
      create: () => {
        try {
          return hasPermission('users', 'create') || hasPermission('user_management', 'write')
        } catch (error) {
          console.error('Error checking users create permission:', error)
          return false
        }
      },
      update: () => {
        try {
          return hasPermission('users', 'update') || hasPermission('user_management', 'write')
        } catch (error) {
          console.error('Error checking users update permission:', error)
          return false
        }
      },
      delete: () => {
        try {
          return hasPermission('users', 'delete') || hasPermission('user_management', 'delete')
        } catch (error) {
          console.error('Error checking users delete permission:', error)
          return false
        }
      }
    },

    // Roles (usar permisos de users como fallback ya que no hay permiso específico de roles)
    roles: {
      view: () => {
        try {
          // Intentar permiso específico de roles, si no existe usar user_management como fallback
          return hasPermission('roles', 'read') || hasPermission('user_management', 'read')
        } catch (error) {
          console.error('Error checking roles view permission:', error)
          return false
        }
      }
      // No create, update, delete ya que los roles son solo lectura
    },

    // Logs (usar 'read' o 'audit' como válidos)
    logs: {
      view: () => {
        try {
          return hasPermission('logs', 'read') || hasPermission('logs', 'audit') || 
                 hasPermission('system_logs', 'read') || hasPermission('system_logs', 'audit')
        } catch (error) {
          console.error('Error checking logs view permission:', error)
          return false
        }
      },
      export: () => {
        try {
          return hasPermission('logs', 'export') || hasPermission('logs', 'read') ||
                 hasPermission('system_logs', 'export') || hasPermission('system_logs', 'read')
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
          return hasPermission('reports', 'read') || hasPermission('reports_analytics', 'read')
        } catch (error) {
          console.error('Error checking reports view permission:', error)
          return false
        }
      },
      generate: () => {
        try {
          // Usar 'write' para generar reportes ya que no hay 'generate' en backend
          return hasPermission('reports', 'write') || hasPermission('reports_analytics', 'write')
        } catch (error) {
          console.error('Error checking reports generate permission:', error)
          return false
        }
      },
      export: () => {
        try {
          return hasPermission('reports', 'export') || hasPermission('reports_analytics', 'export')
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

      const result = routePermissions[routeName] || false
      return result
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
          const hasAccess = route && route.name && canAccessRoute(route.name)
          return hasAccess
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