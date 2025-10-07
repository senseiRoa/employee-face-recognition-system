import { defineStore } from 'pinia'
import api from '../composables/api'

export const useRolesStore = defineStore('roles', {
  state: () => ({
    roles: [],
    loading: false,
    lastFetch: null,
    cacheTimeout: 5 * 60 * 1000 // 5 minutos
  }),

  getters: {
    // Obtener rol por ID
    getRoleById: (state) => (roleId) => {
      return state.roles.find(role => role.id === roleId)
    },

    // Obtener permisos de un rol específico
    getRolePermissions: (state) => (roleId) => {
      const role = state.roles.find(role => role.id === roleId)
      return role?.permissions || []
    },

    // Verificar si un rol tiene un permiso específico
    hasPermission: (state) => (roleId, permission, action = null) => {
      try {
        if (!state.roles || state.roles.length === 0) return false
        const role = state.roles.find(role => role.id === roleId)
        if (!role || !role.permissions) return false

        const perm = role.permissions.find(p => p.permission === permission)
        if (!perm) return false

        // Si no se especifica acción, solo verificar que existe el permiso
        if (!action) return true

        // Verificar acción específica
        return perm.actions && perm.actions.includes(action)
      } catch (error) {
        console.error('Error in hasPermission getter:', error)
        return false
      }
    },

    // Verificar múltiples permisos
    hasAnyPermission: (state) => (roleId, permissions) => {
      try {
        if (!state.roles || state.roles.length === 0 || !permissions) return false
        return permissions.some(({ permission, action }) => 
          state.hasPermission(roleId, permission, action)
        )
      } catch (error) {
        console.error('Error in hasAnyPermission getter:', error)
        return false
      }
    },

    // Obtener todos los permisos únicos disponibles
    allPermissions: (state) => {
      const permissionsSet = new Set()
      state.roles.forEach(role => {
        role.permissions.forEach(perm => {
          permissionsSet.add(perm.permission)
        })
      })
      return Array.from(permissionsSet)
    }
  },

  actions: {
    // Cargar roles desde la API
    async fetchRoles(force = false) {
      // Verificar cache
      if (!force && this.lastFetch && 
          Date.now() - this.lastFetch < this.cacheTimeout) {
        return this.roles
      }

      this.loading = true
      try {
        const response = await api.get('/roles/?skip=0&limit=100')
        this.roles = response.data
        this.lastFetch = Date.now()
        return this.roles
      } catch (error) {
        console.error('Error fetching roles:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // Limpiar cache
    clearCache() {
      this.lastFetch = null
    },

    // Refrescar roles
    async refreshRoles() {
      return this.fetchRoles(true)
    }
  }
})