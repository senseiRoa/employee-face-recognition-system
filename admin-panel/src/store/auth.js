import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/composables/api'
import { useRolesStore } from './roles'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    loading.value = true
    try {
      const loginData = {
        username_or_email: credentials.username,
        password: credentials.password
      }

      const response = await api.post('/auth/login', loginData)

      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      // Configurar el token para futuras peticiones
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      // Cargar roles después del login exitoso
      const rolesStore = useRolesStore()
      try {
        await rolesStore.fetchRoles()
      } catch (error) {
        console.warn('Could not load roles after login:', error)
      }
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error de autenticación' 
      }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete api.defaults.headers.common['Authorization']
    
    // Limpiar cache de roles
    const rolesStore = useRolesStore()
    rolesStore.clearCache()
  }

  const initAuth = () => {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      
      // Cargar roles si ya estamos autenticados
      const rolesStore = useRolesStore()
      rolesStore.fetchRoles().catch(error => {
        console.warn('Could not load roles on init:', error)
      })
    }
  }

  return {
    token,
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    initAuth
  }
})