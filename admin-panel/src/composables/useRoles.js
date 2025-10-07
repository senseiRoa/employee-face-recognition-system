import { computed } from 'vue'
import { useRolesStore } from '../store/roles'
import { useToast } from 'vue-toastification'

export function useRoles() {
  const rolesStore = useRolesStore()
  const toast = useToast()

  // Estados reactivos del store
  const roles = computed(() => rolesStore.roles)
  const loading = computed(() => rolesStore.loading)

  const fetchRoles = async () => {
    try {
      await rolesStore.fetchRoles()
    } catch (error) {
      toast.error('Error loading roles')
      console.error('Error fetching roles:', error)
    }
  }

  // Función para refrescar roles
  const refreshRoles = async () => {
    try {
      await rolesStore.refreshRoles()
      toast.success('Roles refreshed successfully')
    } catch (error) {
      toast.error('Error refreshing roles')
      console.error('Error refreshing roles:', error)
    }
  }

  // Obtener rol por ID
  const getRoleById = (roleId) => {
    return rolesStore.getRoleById(roleId)
  }

  // Obtener permisos de un rol
  const getRolePermissions = (roleId) => {
    return rolesStore.getRolePermissions(roleId)
  }

  return {
    // Estados
    roles,
    loading,

    // Funciones de lectura únicamente
    fetchRoles,
    refreshRoles,
    getRoleById,
    getRolePermissions,

    // Acceso directo al store si se necesita
    rolesStore
  }
}