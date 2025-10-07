import { computed } from 'vue'
import { usePermissions } from './usePermissions'

/**
 * Composable reutilizable para manejar permisos en las vistas
 * @param {string} module - El módulo de permisos (companies, users, employees, etc.)
 * @returns {object} Objeto con computed properties para cada acción
 */
export function useViewPermissions(module) {
  const permissions = usePermissions()

  if (!module || !permissions.permissions[module]) {
    console.warn(`Module '${module}' not found in permissions`)
    return {
      canView: computed(() => false),
      canCreate: computed(() => false),
      canUpdate: computed(() => false),
      canDelete: computed(() => false),
      canExport: computed(() => false),
      hasAnyAction: computed(() => false)
    }
  }

  const modulePermissions = permissions.permissions[module]

  const canView = computed(() => {
    try {
      return modulePermissions.view ? modulePermissions.view() : true
    } catch (error) {
      console.warn(`Error checking view permission for ${module}:`, error)
      return false
    }
  })

  const canCreate = computed(() => {
    try {
      return modulePermissions.create ? modulePermissions.create() : false
    } catch (error) {
      console.warn(`Error checking create permission for ${module}:`, error)
      return false
    }
  })

  const canUpdate = computed(() => {
    try {
      return modulePermissions.update ? modulePermissions.update() : false
    } catch (error) {
      console.warn(`Error checking update permission for ${module}:`, error)
      return false
    }
  })

  const canDelete = computed(() => {
    try {
      return modulePermissions.delete ? modulePermissions.delete() : false
    } catch (error) {
      console.warn(`Error checking delete permission for ${module}:`, error)
      return false
    }
  })

  // Permisos especiales según el módulo
  const canExport = computed(() => {
    try {
      return modulePermissions.export ? modulePermissions.export() : false
    } catch (error) {
      console.warn(`Error checking export permission for ${module}:`, error)
      return false
    }
  })

  const canRegisterFace = computed(() => {
    try {
      return modulePermissions.registerFace ? modulePermissions.registerFace() : false
    } catch (error) {
      console.warn(`Error checking registerFace permission for ${module}:`, error)
      return false
    }
  })

  // Si el usuario tiene al menos una acción disponible
  const hasAnyAction = computed(() => {
    return canCreate.value || canUpdate.value || canDelete.value || canExport.value
  })

  return {
    canView,
    canCreate,
    canUpdate,
    canDelete,
    canExport,
    canRegisterFace,
    hasAnyAction,
    // Para debugging
    modulePermissions,
    module
  }
}

/**
 * Función helper para obtener un mensaje cuando no hay acciones disponibles
 * @param {object} permissions - Objeto de permisos del useViewPermissions
 * @returns {string} Mensaje a mostrar
 */
export function getNoActionsMessage(permissions) {
  if (!permissions.hasAnyAction.value) {
    return 'No actions available'
  }
  return ''
}

/**
 * Función helper para verificar si se debe mostrar la columna de acciones
 * @param {object} permissions - Objeto de permisos del useViewPermissions
 * @returns {boolean} Si mostrar la columna
 */
export function shouldShowActionsColumn(permissions) {
  return permissions.hasAnyAction.value
}