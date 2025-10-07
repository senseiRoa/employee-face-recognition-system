import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePermissions } from './usePermissions'
import { useToast } from 'vue-toastification'

export function useAccessControl() {
  const router = useRouter()
  const permissions = usePermissions()
  const toast = useToast()

  // Verificar acceso a una acción específica
  const checkAccess = (permission, action = null, showToast = true) => {
    const hasAccess = permissions.hasPermission(permission, action)
    
    if (!hasAccess && showToast) {
      toast.error('You do not have permission to perform this action')
    }
    
    return hasAccess
  }

  // Verificar acceso a múltiples permisos (OR logic)
  const checkAnyAccess = (permissionsList, showToast = true) => {
    const hasAccess = permissions.hasAnyPermission(permissionsList)
    
    if (!hasAccess && showToast) {
      toast.error('You do not have permission to perform this action')
    }
    
    return hasAccess
  }

  // Verificar acceso a ruta
  const checkRouteAccess = (routeName, showToast = true) => {
    const hasAccess = permissions.canAccessRoute(routeName)
    
    if (!hasAccess && showToast) {
      toast.error('You do not have permission to access this page')
    }
    
    return hasAccess
  }

  // Redirigir si no tiene acceso
  const requireAccess = (permission, action = null, redirectTo = '/admin/dashboard') => {
    if (!checkAccess(permission, action)) {
      router.push(redirectTo)
      return false
    }
    return true
  }

  // Verificar y ejecutar acción
  const withPermission = async (permission, action, callback, showToast = true) => {
    if (checkAccess(permission, action, showToast)) {
      try {
        return await callback()
      } catch (error) {
        console.error('Error executing action:', error)
        throw error
      }
    }
    return null
  }

  // Estados reactivos para UI
  const uiPermissions = computed(() => ({
    // Dashboard
    canViewDashboard: permissions.permissions.dashboard.view(),

    // Companies
    canViewCompanies: permissions.permissions.companies.view(),
    canCreateCompany: permissions.permissions.companies.create(),
    canUpdateCompany: permissions.permissions.companies.update(),
    canDeleteCompany: permissions.permissions.companies.delete(),

    // Warehouses
    canViewWarehouses: permissions.permissions.warehouses.view(),
    canCreateWarehouse: permissions.permissions.warehouses.create(),
    canUpdateWarehouse: permissions.permissions.warehouses.update(),
    canDeleteWarehouse: permissions.permissions.warehouses.delete(),

    // Employees
    canViewEmployees: permissions.permissions.employees.view(),
    canCreateEmployee: permissions.permissions.employees.create(),
    canUpdateEmployee: permissions.permissions.employees.update(),
    canDeleteEmployee: permissions.permissions.employees.delete(),
    canRegisterFace: permissions.permissions.employees.registerFace(),

    // Users
    canViewUsers: permissions.permissions.users.view(),
    canCreateUser: permissions.permissions.users.create(),
    canUpdateUser: permissions.permissions.users.update(),
    canDeleteUser: permissions.permissions.users.delete(),

    // Roles
    canViewRoles: permissions.permissions.roles.view(),

    // Logs
    canViewLogs: permissions.permissions.logs.view(),
    canExportLogs: permissions.permissions.logs.export(),

    // Reports
    canViewReports: permissions.permissions.reports.view(),
    canGenerateReports: permissions.permissions.reports.generate(),
    canExportReports: permissions.permissions.reports.export()
  }))

  // Componente HOC para proteger acciones
  const ProtectedAction = {
    props: {
      permission: { type: String, required: true },
      action: { type: String, default: null },
      fallback: { type: Boolean, default: false }
    },
    setup(props, { slots }) {
      const hasAccess = computed(() => 
        permissions.hasPermission(props.permission, props.action)
      )

      return () => {
        if (hasAccess.value) {
          return slots.default?.()
        } else if (props.fallback && slots.fallback) {
          return slots.fallback?.()
        }
        return null
      }
    }
  }

  return {
    // Funciones de verificación
    checkAccess,
    checkAnyAccess,
    checkRouteAccess,
    requireAccess,
    withPermission,

    // Estados para UI
    uiPermissions,

    // Componente de protección
    ProtectedAction,

    // Referencias a otros composables
    permissions
  }
}