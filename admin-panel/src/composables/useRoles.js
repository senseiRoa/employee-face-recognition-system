import { ref } from 'vue'
import api from './api'
import { useToast } from 'vue-toastification'

export function useRoles() {
  const roles = ref([])
  const loading = ref(false)
  const toast = useToast()

  const fetchRoles = async () => {
    loading.value = true
    try {
      const response = await api.get('/roles/')
      roles.value = response.data
    } catch (error) {
      toast.error('Error loading roles')
      console.error('Error fetching roles:', error)
    } finally {
      loading.value = false
    }
  }

  const createRole = async (roleData) => {
    loading.value = true
    try {
      const response = await api.post('/roles/', roleData)
      roles.value.push(response.data)
      toast.success('Role created successfully')
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error creating role')
      return { success: false, error: error.response?.data?.detail || 'Unknown error' }
    } finally {
      loading.value = false
    }
  }

  const updateRole = async (id, roleData) => {
    loading.value = true
    try {
      const response = await api.put(`/roles/${id}`, roleData)
      const index = roles.value.findIndex(r => r.id === id)
      if (index !== -1) {
        roles.value[index] = response.data
      }
      toast.success('Role updated successfully')
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error updating role')
      return { success: false, error: error.response?.data?.detail || 'Unknown error' }
    } finally {
      loading.value = false
    }
  }

  const deleteRole = async (id) => {
    loading.value = true
    try {
      await api.delete(`/roles/${id}`)
      roles.value = roles.value.filter(r => r.id !== id)
      toast.success('Role deleted successfully')
      return { success: true }
    } catch (error) {
      toast.error('Error deleting role')
      return { success: false, error: error.response?.data?.detail || 'Unknown error' }
    } finally {
      loading.value = false
    }
  }

  const getRole = async (id) => {
    loading.value = true
    try {
      const response = await api.get(`/roles/${id}`)
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error getting role')
      return { success: false, error: error.response?.data?.detail || 'Unknown error' }
    } finally {
      loading.value = false
    }
  }

  return {
    roles,
    loading,
    fetchRoles,
    createRole,
    updateRole,
    deleteRole,
    getRole
  }
}